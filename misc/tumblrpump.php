<?php
// Simple Tumblr API client.
// Written by Justin Forest, 24/04/2009.
// Public domain.

class Tumblr
{
  private $host;
  private $user;
  private $pass;
  private $posts = array();

  public function __construct($host, $user = null, $pass = null)
  {
    $parts = parse_url($host);
    if (1 == count($parts) and isset($parts['path']))
      $parts['host'] = $parts['path'];

    if (!isset($parts['host']))
      throw new InvalidArgumentException(t('Invalid tumblr host: ' . $host));

    $this->host = $parts['host'];
    $this->user = $user;
    $this->pass = $pass;
  }

  public function read($type = null)
  {
    $posts = array();

    $api = 'http://' . $this->host . '/api/read';

    for ($start = 0, $num = 20; true; $start += $num) {
      $url = $api . '?start=' . $start . '&num=' . $num;

      if (null !== $type)
        $url .= '&type=' . urlencode($type);

      $this->log('reading from ' . $url);

      if (false === ($xml = @file_get_contents($url)))
        throw new RuntimeException("{$this->host} does not look like a tumblr blog.");

      $em = new SimpleXMLElement($xml);

      if ('1.0' !== (string)$em->attributes()->version)
        throw new Exception("Wrong API version at {$this->host}.");

      if (null === $em->posts->post[0])
        break;

      for ($idx = 0; $em->posts->post[$idx]; $idx++) {
        $post = $em->posts->post[$idx];

        $tmp = array(
          'type' => (string)$post->attributes()->type,
          'date' => (string)$post->attributes()->{'date-gmt'},
          'tags' => array(),
          'format' => (string)$post->attributes()->format,
          );

        foreach ($post->tag as $t)
          $tmp['tags'][] = (string)$t;

        $prefix = $tmp['type'] . '-';
        foreach ($post as $k => $v)
          if (0 === strpos((string)$k, $prefix))
            if (!array_key_exists($key = substr((string)$k, strlen($prefix)), $tmp))
              $tmp[$key] = (string)$v;

        // Additional processing for some types.
        switch ($tmp['type']) {
        case 'photo':
          if (isset($tmp['url'])) {
            $tmp['source'] = $tmp['url'];
            unset($tmp['url']);
          }
          if (isset($tmp['link-url'])) {
            $tmp['click-through-url'] = $tmp['link-url'];
            unset($tmp['link-url']);
          }
        }

        array_unshift($posts, $tmp);
      }
    }

    $this->log(sprintf('read %u posts from %s', count($posts), $this->host));

    return $posts;
  }

  public function post(array $post)
  {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, 'http://www.tumblr.com/api/write');
    curl_setopt($ch, CURLOPT_FAILONERROR, 0);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $this->getPostData($post));

    $output = curl_exec($ch);
    $info = curl_getinfo($ch);
    curl_close($ch);

    if ($info['http_code'] > 300)
      throw new RuntimeException(sprintf("ERROR %s: %s", $info['http_code'], $output));

    if (empty($post['private']))
      $this->log(sprintf("created http://%s/post/%s", $this->host, $output));
    else
      $this->log(sprintf("created http://www.tumblr.com/edit/%s", $output));
  }

  protected function log($message)
  {
    error_log($message);
  }

  private function getPostData(array $post)
  {
    if (isset($post['tags'])) {
      if (!is_array($post['tags']))
        throw new InvalidArgumentException('Post tags must be an array.');
      $post['tags'] = implode(',', $post['tags']);
    }

    $post['email'] = $this->user;
    $post['password'] = $this->pass;
    $post['group'] = $this->host;
    if (!isset($post['generator']))
      $post['generator'] = 'Tumblr.php';

    $fields = array();
    foreach ($post as $k => $v)
      $fields[] = $k . '=' . rawurlencode($v);

    return implode('&', $fields);
  }
}

// Unfortunately, getopt() is cross-platform only since 5.3.0.
function get_args(array $argv)
{
  $url = null;
  $args = array();
  $program = basename(array_shift($argv));

  while (!empty($argv)) {
    switch ($option = array_shift($argv)) {
    case '-b':
      $key = 'to';
      break;
    case '-e':
      $key = 'login';
      break;
    case '-p':
      $key = 'password';
      break;
    case '-t':
      $key = 'tags';
      break;
    case '-h':
      $key = 'hidden';
      array_unshift($argv, true);
      break;
    case '-l':
      $key = 'limit';
      break;
    case '-f':
      $key = 'type';
      break;
    default:
      if ('-' == substr($option, 0, 1)) {
        $args = array();
        break 2;
      }
      $key = 'from';
      array_unshift($argv, $option);
    }

    $args[$key] = array_shift($argv);
  }

  foreach (array('to', 'from', 'login', 'password') as $key)
    if (!isset($args[$key]))
      die(sprintf("Usage: {$program} old_url OPTIONS\n"
        . "Options:\n"
        . "  -b blog_name  - new blog host name, e.g.: demo.tumblr.com\n"
        . "  -e email      - your tumblr login, e.g.: john@example.com\n"
        . "  -p password   - your tumblr password\n"
        . "  -t tags       - extra tags for all posts\n"
        . "  -h            - create private posts\n"
        . "  -l limit      - copy only as many posts\n"
        . "  -f type       - copy only such posts (audio, video, photo, regular, link)\n"
        ));

  return $args;
}

function main(array $argv)
{
  try {
    $args = get_args($argv);

    $src = new Tumblr($args['from']);
    $dst = new Tumblr($args['to'], $args['login'], $args['password']);

    $filter = isset($args['type'])
      ? $args['type']
      : null;

    $count = 0;
    foreach ($src->read($filter) as $post) {
      if (!empty($args['tags']))
        $post['tags'][] = $args['tags'];
      if (!empty($args['hidden']))
        $post['private'] = 1;

      try {
        $dst->post($post);
        $count++;

        if (isset($args['limit']) and $count >= $args['limit']) {
          printf("Copied %u posts, aborting.\n", $count);
          break;
        }
      } catch (Exception $e) {
        printf("Error posting something of type '%s': %s.\n", $post['type'], rtrim($e->getMessage(), '.'));
        var_dump($post);
      }
    }

    printf("OK\n");
  } catch (Exception $e) {
    printf("ERROR: %s.\n", rtrim($e->getMessage(), '.'));
    exit(1);
  }
}

return main($argv);
