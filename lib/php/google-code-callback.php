<?php
/**
 * Гейт Google Code => Мегаплан.
 *
 * @url http://code.google.com/p/support/wiki/PostCommitWebHooks
 */

class Megaplan_GoogleCode_HookHandler
{
    /**
     * Имя файла, в которых сохраняется и из которого загружается при повторах
     * содержимое запроса.
     *
     * @var string
     */
    protected $dump_filename;

    /**
     * Имя конфигурационного файла.
     *
     * @var string
     */
    protected $config_filename;

    /**
     * Содержимое конфигурационного файла.
     *
     * @var array
     */
    protected $config_data;

    /**
     * Инициализация обработчика.
     *
     * Определяет имя файла с дампом, загружает конфиг итд.
     */
    public function __construct()
    {
        $this->dump_filename = substr(__FILE__, 0, -3) . 'txt';
        $this->config_filename = substr(__FILE__, 0, -3) . 'inc';

        ini_set('error_log', substr(__FILE__, 0, -3) . 'log');
        error_reporting(E_ALL);

        $this->loadConfig();
    }

    /**
     * Обрабатывает или повторяет запрос в зависимости от способа запуска: при
     * запуске через веб ищет данные в POST, при запуске из консоли пытается
     * воспроизвести последний запрос, приходивший через веб.
     */
    public function process_request()
    {
        if (php_sapi_name() != 'cli')
            $this->processWebRequest();
        else
            $this->processConsoleRequest();
    }

    /**
     * Обработка запроса, поступившего через веб.
     *
     * Перед началом обработки отключается от пользователя, если используется
     * PHP-FPM.
     */
    protected function processWebRequest()
    {
        header('HTTP/1.1 200 OK');
        header('Content-Type: text/plain; charset=utf-8');

        try {
            $data = $this->getPayload();
            if (false === $data)
                throw new Exception("Could not decode your request.");

            // http://php-fpm.org/wiki/Features#fastcgi_finish_request.28.29
            if (function_exists('fastcgi_finish_request'))
                fastcgi_finish_request();

            $this->processPayload($data);
        } catch (Exception $e) {
            print $e->getMessage();
        }
    }

    /**
     * Загружает и обрабатывает содержимое последнего запроса, пришедшего из
     * Гугла.
     */
    protected function processConsoleRequest()
    {
        try {
            if (!file_exists($this->dump_filename))
                throw new Exception(sprintf("Could not replay: file %s not found.", $this->dump_filename));
            $this->processPayload(json_decode(file_get_contents($this->dump_filename)));
        } catch (Exception $e) {
            die($e->getMessage());
        }
    }

    /**
     * Вытаскивает содержимое запроса из окружения.
     *
     * @return mixed Массив с содержимым или FALSE, если не удалось его достать
     * или провалидировать.
     */
    protected function getPayload()
    {
        if (empty($_SERVER["HTTP_GOOGLE_CODE_PROJECT_HOSTING_HOOK_HMAC"]))
            return false;

        $project_name = $_GET['project'];
        if (empty($this->config_data[$project_name]['key']))
            throw new Exception("Project {$project_name} not configured.");

        $key = $this->config_data[$project_name]['key'];
        $raw_data = file_get_contents("php://input");

        $digest = hash_hmac("md5", $raw_data, $key);
        if ($digest != $_SERVER["HTTP_GOOGLE_CODE_PROJECT_HOSTING_HOOK_HMAC"])
            return false;

        file_put_contents($this->dump_filename, $raw_data);
        return json_decode($raw_data);
    }

    /**
     * Обработка запроса.
     *
     * Вызывает processRevision для каждой ревизии.
     *
     * @param mixed $data Исходные данные запроса (декодированное содержимое
     * JSON).
     */
    protected function processPayload($data)
    {
        $project_name = $data->project_name;
        foreach ($data->revisions as $revision)
            $this->processRevision($project_name, $revision);
    }

    /**
     * Обработка отдельной ревизии.
     *
     * @param string $project_name Имя проекта в GC.
     * @param object $revision Описание ревизии.
     */
    protected function processRevision($project_name, $revision)
    {
        $author = $revision->author;
        $message = $revision->message;

        if (preg_match('/^(?:Fixes|Update) issue (\d+)(.*)/smi', $message, $m)) {
            $task_id = $this->getMegaplanTaskId($m[1]);
            if ($task_id) {
				$message = $m[2];
                $time_taken = $this->getTimeTaken($message);
                $message = $this->stripGoogleIssueModifiers(trim($message));
                $message .= "\n\nhttp://code.google.com/p/molinos-cms/source/detail?r=" . substr($revision->revision, 0, 12);
                $this->updateMegaplan($project_name, $task_id, $author, $message, $time_taken);
            }
        }
    }

    /**
     * Отправляет изменение в Мегаплан.
     *
     * @param string $project_name Имя проекта в Гугле.
     * @param int $task_id Идентификатор задачи в Мегаплане.
     * @param string $author Логин автора в Гугле.
     * @param string $comment Комментарий для Мегаплана.
     * @param int $time_taken Затраченное время, в минутах.
     */
    protected function updateMegaplan($project_name, $task_id, $author, $comment, $time_taken)
    {
        if (empty($this->config_data[$project_name]['users'][$author]))
            throw new Exception("User {$author} is not configured.");

        $auth = array(
            'host' => $this->config_data[$project_name]['megaplan'],
            'access_id' => $this->config_data[$project_name]['users'][$author]['access_id'],
            'secret_key' => $this->config_data[$project_name]['users'][$author]['secret_key'],
            );

        return $this->callMegaplanAPI('BumsCommonApiV01/Comment/create.api', array(
            'SubjectType' => 'task',
            'SubjectId' => 1000000 + $task_id,
            'Model[Text]' => $comment,
            'Model[Work]' => $time_taken,
            ), $auth);
    }

    /**
     * Отправляет произвольный запрос в Мегаплан.
     *
     * Самодостаточная функция.
     *
     * @param string $method Имя вызываемого метода.
     * @param array $data Передаваемые методу данные.
     * @param array $auth Параметры аутентификации, должны содержать ключи host,
     * access_id и secret_key.
     * @param bool $signed Значение false отключает подписывание запросов.
     * @return array Ответ сервера.
     */
    protected function callMegaplanAPI($method, array $data, array $auth, $signed = true)
    {
        $headers = array(
            'Date' => date('r'),
            'Content-Type' => 'application/x-www-form-urlencoded',
            'Accept' => 'application/json',
            'User-Agent' => 'SdfApi_Request',
            );

        // Подписываем результат.
        if ($signed) {
            $signature = base64_encode(hash_hmac('sha1',
                "POST\n\n{$headers['Content-Type']}\n{$headers['Date']}\n{$auth['host']}/{$method}",
                $auth['secret_key']));
            $headers['X-Authorization'] = $auth['access_id'] . ':' . $signature;
        }

        // Кодируем заголовки в строку.
        $str_headers = '';
        foreach ($headers as $k => $v)
            $str_headers .= $k . ': ' . $v . PHP_EOL;

        // Выполняем запрос.
        $url = "https://{$auth['host']}/{$method}";
        $ctx = stream_context_create(array(
            'http' => array(
                'method' => 'POST',
                'header' => $str_headers,
                'content' => http_build_query($data),
                ),
            ));
        $response = file_get_contents($url, false, $ctx);

        return json_decode($response);
    }

    /**
     * Определяет идентификатор проблемы в Мегаплане.
     *
     * @param int $google_issue_id Идентификатор проблемы в Гугле.
     * @return int Идентификатор проблемы в Мегаплане или NULL.  Идентификатор
     * указывается меткой Megaplan-123.
     */
    protected function getMegaplanTaskId($google_issue_id)
    {
        $lines = explode("\n", @file_get_contents("http://code.google.com/p/molinos-cms/issues/csv?can=1&q=id%3A{$google_issue_id}&colspec=Task"));
        if (empty($lines[1]))
            return null;
        $task_id = trim($lines[1], '"');
        return $task_id;
    }

    /**
     * Определяет время, затраченное на работу.
     *
     * @param string &$message Комментарий к коммиту.  Если указание времени
     * найдено, оно удаляется.
     * @return int Время в минутах, 0 если неизвестно.
     */
    protected function getTimeTaken(&$message)
    {
        $work = 0;
        if (preg_match('/^(⌚|Time:)\s+(\d+)$/mi', $message, $m)) {
            $work = floatval($m[2]) / 60;
            $comment = trim(str_replace($m[0], '', $message));
        }
        return $work;
    }

    /**
     * Удаление модификаторов состояния задачи.
     *
     * @param string $message Описание коммита.
     * @return string Комментарий для Мегаплана.
     */
    protected function stripGoogleIssueModifiers($message)
    {
        $lines = explode("\n", $message);

        while (true) {
            $parts = explode(': ', $lines[0]);
            if (count($parts) < 2)
                break;
            if (!in_array(mb_strtolower($parts[0]), array('status', 'labels', 'time')))
                break;
            array_shift($lines);
        }

        return trim(implode("\n", $lines));
    }

    /**
     * Saves request contents to a file.
     */
    protected function saveRequest()
    {
        $data = var_export(array(
            'get' => $_GET,
            'post' => $_POST,
            'server' => $_SERVER,
            ), true);
        file_put_contents($this->dump_filename, $data);
    }

    /**
     * Загрузка конфигурационного файла.
     *
     * Имя файла указано в $this->config_filename.  Если файл не существует или
     * не содержит PHP массив, возникает исключение.
     */
    protected function loadConfig()
    {
        if (!file_exists($this->config_filename))
            throw new Exception("Config file {$this->config_filename} not found.");
        if (!is_array($this->config_data = @include $this->config_filename))
            throw new Exception("Config file {$this->config_filename} has bad contents.");
    }
}

$handler = new Megaplan_GoogleCode_HookHandler();
$handler->process_request();
