<?php
/**
 * Обработчик уведомлений от BitBucket.
 *
 * Используется для связи bitbucket.org с Мегапланом.  При получении сообщения
 * о коммите, содержащего фразу "task номер", отправляет к этой задаче
 * комментарий.  В качестве текста комментария используется всё, что идёт после
 * строки с указанием задачи.  Пример комментария к коммиту:
 *
 *   Исправлена опечатка.
 *
 *   Update issue 713
 *   Исправлена опечатка, в связи с которой не работала какая-то функция.
 *   Теперь всё должно работать.
 *
 *
 * Настройки хранятся в файле bitbucket-megaplan-gw.inc (расширение скрипта
 * заменяется на inc), который должен быть следующего вида:
 *
 *   <?php return array(
 *     'repos' => array(
 *       'owner/repo' => array('host' => 'xyz.megaplan.ru'),
 *       ),
 *     'committers' => array(
 *       'john.doe' => array('access_id' => 'abc', 'secret_key' => 'xyz'),
 *       ),
 *     );
 *
 *
 * Для получения ключей нужно выполнить этот скрипт в консоли с параметром
 * auth: php -f script.php auth.  К этому моменту должен существовать
 * конфигурационный файл с описанием доступных репозиториев, т.к. эта
 * информация нужна для аутентификации в Мегаплане.
 *
 *
 * @author hex@umonkey.net (Justin Forest)
 * @copyright Public Domain
 * @url http://wiki.megaplan.ru/API_rules
 */


/**
 * Сохраняет содержимое запроса в текстовый файл для отладочных целей.
 */
function dump_request()
{
    $data = var_export(array(
        'get' => $_GET,
        'post' => $_POST,
        'files' => $_FILES,
        'server' => $_SERVER,
        ), true);

    $filename = substr(__FILE__, 0, -3) . '.txt';
    file_put_contents($filename, $data);
}


/**
 * Загружает конфигураицонный файл.
 *
 * Если файл отсутствует, возникает исключение.
 *
 * @return array Содержимое файла.
 */
function load_config()
{
	$config = @include substr(__FILE__, 0, -3) . 'inc';
	if (false === $config)
		send_error('Config file not found.');
	return $config;
}


/**
 * Декодирует содержимое запроса и применяет.
 *
 * @param string $payload Запрос в JSON.
 */
function process_request($payload)
{
	if ('cli' != php_sapi_name())
		dump_request();

    $config = load_config();
    $data = json_decode($payload);

    $repo_user = $data->repository->owner;
    $repo_name = $data->repository->name;

    $tmp = $repo_user . '/' . $repo_name;
    if (!isset($config['repos'][$tmp]))
        send_error("This repository is not configured.");
    $megaplan_host = $config['repos'][$tmp]['host'];

    foreach ($data->commits as $commit) {
        if (!isset($config['committers'][$commit->author]))
            error_log("Committer {$commit->author} is not configured.");

        elseif (preg_match('@^Update issue (\d+)(.*)@sim', $commit->message, $m)) {
            $issue_id = intval($m[1]);
            $comment = trim($m[2]) . "\n\n" . "https://bitbucket.org/{$repo_user}/{$repo_name}/changeset/{$commit->node}";

            $auth = $config['committers'][$commit->author];
            $auth['host'] = $megaplan_host;

            update_mp_issue($issue_id, $comment, $auth);
        }
    }
}


/**
 * Отправляет комментарий в Мегаплан.
 *
 * @param string $host Доменное имя инсталляции Мегаплана.
 * @param int $issue_id Идентификатор обновляемой задачи в Мегаплане.  К нему
 * прибавляется 1,000,000.
 * @param string $comment Текст добавляемого комментария.
 * @param array $auth Параметры аутентификации.  Используются элементы с
 * ключами host, access_id, secret_key.
 */
function update_mp_issue($issue_id, $comment, array $auth)
{
    return send_megaplan_request('BumsCommonApiV01/Comment/create.api', array(
        'SubjectType' => 'task',
        'SubjectId' => 1000000 + $issue_id,
        'Model[Text]' => $comment,
        ), $auth);
}


/**
 * Выводит сообщение об ошибке.
 *
 * При запуске из консоли выводит сообщение в stderr.
 *
 * @param string $message Текст сообщения.
 * @param int $status Код ошибки.
 */
function send_error($message, $status = 500)
{
    if ('cli' == php_sapi_name())
        die(file_put_contents('php://stderr', trim($message) . "\n"));
    header("HTTP/1.0 {$status} Error");
    header('Content-Type: text/plain; charset=utf-8');
    die($message);
}


/**
 * Отправляет произвольный запрос в Мегаплан.
 *
 * @param string $method Имя вызываемого метода.
 * @param array $data Передаваемые методу данные.
 * @param array $auth Параметры аутентификации, должны содержать ключи host,
 * access_id и secret_key.
 * @param bool $signed Значение false отключает подписывание запросов.
 * @return array Ответ сервера.
 */
function send_megaplan_request($method, array $data, array $auth, $signed = true)
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
 * Аутентификация пользователя.
 *
 * @param array $argv Параметры командной строки.  Требуемая
 * последовательность: repo_name, user_name, megaplan_login, megaplan_password.
 */
function auth_user(array $argv)
{
	if (count($argv) != 6)
		send_error("Usage: php -f {$argv[0]} {$argv[1]} repo/name bitbucket_login megaplan_login megaplan_password");

	$config = load_config();

	if (empty($config['repos'][$argv[2]]))
		send_error("Repo {$argv[2]} not defined.");

	$auth = array(
		'host' => $config['repos'][$argv[2]]['host'],
		);

	$data = array(
		'Login' => $argv[4],
		'Password' => md5($argv[5]),
		);

	$resp = send_megaplan_request('BumsCommonApiV01/User/authorize.api', $data, $auth, false);
	if ($resp->status->code == 'ok') {
		$config['committers'][$argv[3]]['access_id'] = $resp->data->AccessId;
		$config['committers'][$argv[3]]['secret_key'] = $resp->data->SecretKey;

		$config_data = '<?php return ' . var_export($config, true) . ';';
		file_put_contents(substr(__FILE__, 0, -3) . 'inc', $config_data);

		print "OK\n";
	}
}


if ('cli' != php_sapi_name()) {
    if (empty($_POST['payload']))
        send_error('No payload.');
    process_request($_POST['payload']);
} elseif (@$argv[1] == 'auth') {
	auth_user($argv);
}
