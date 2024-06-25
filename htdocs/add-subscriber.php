<?php
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0, Cache-Control: post-check=0, pre-check=0');
header('Pragma: no-cache');

if (file_exists('production-config.php')) {
    require_once 'production-config.php';
} else {
    define('API_BASE_URL', getenv('API_BASE_URL') ?: 'https://api.systeme.io');
    define('API_KEY', getenv('API_KEY') ?: null);
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!API_BASE_URL || !API_KEY) {
        # Misconfigured; redirect to self in the diagnose mode
        header("HTTP/1.1 303");
        header("Location: /add-subscriber.php");
    } else {
        handlePost();
    }
} elseif ($_SERVER['REQUEST_METHOD'] === 'GET') {
    diagnose();
} else {
    header("HTTP/1.1 405 Method Not Allowed");
}

function postToAPI($url, $data) {
    $data_string = json_encode($data);
    $ch = curl_init($url);
    if ($ch === false) {
        return [null, 'curl_init failed'];
    }
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'POST');
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data_string);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json',
        'Content-Length: ' . strlen($data_string),
        'X-Api-Key: ' . API_KEY,
    ]);
    $result = curl_exec($ch);
    if ($result !== false) {
        $status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        return [$status, json_decode($result)];
    } else {
        $error = curl_error($ch);
        curl_close($ch);
        return [null, 'curl_exec failed: ' . $error];
    }
}

function getFromAPI($url) {
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'X-Api-Key: ' . API_KEY,
    ]);
    $result = curl_exec($ch);
    if ($result !== false) {
        $status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        return [$status, json_decode($result)];
    } else {
        $error = curl_error($ch);
        curl_close($ch);
        return [null, 'curl_exec failed: ' . $error];
    }
}

function getContactByEmail($email) {
    $path = '/api/contacts';
    $url = API_BASE_URL . $path;
    [$status, $response] = getFromAPI("$url?email=$email");
    if ($status == 200) {
        return $response->items[0] ?? null;
    } else {
        return null;
    }
}

function addContact($email) {
    $path = '/api/contacts';
    $url = API_BASE_URL . $path;
    $data = ['email' => $email];
    [$status, $response] = postToAPI($url, $data);
    if ($status == 201) {
        return $response ?? null;
    } else {
        return null;
    }
}

function getTagByName($tag) {
    $path = '/api/tags';
    $url = API_BASE_URL . $path;
    [$status, $response] = getFromAPI("$url?query=$tag");
    if ($status == 200) {
        return $response->items[0] ?? null;
    } else {
        return null;
    }
}

function assignTagToContact($contact_id, $tag_id) {
    $path = "/api/contacts/$contact_id/tags";
    $url = API_BASE_URL . $path;
    $data = ['tagId' => $tag_id];
    [$status] = postToAPI($url, $data);
    # 204 No Content (there is no response body)
    return ($status == 204);
}

function validateAndSplitTags($tagsString) {
    $tagsString = preg_replace('/\s+/', '', $tagsString);
    if (empty($tagsString)) {
        return [];
    }

    $validTags = [];
    $tags = explode(',', $tagsString);
    foreach ($tags as $tag) {
        if (preg_match('/^[a-zA-Z0-9_-]+$/', $tag) && strlen($tag) > 0) {
            $validTags[] = $tag;
        } else {
            throw new Exception("Invalid tag: $tag");
        }
    }

    return $validTags;
}

function handlePost() {
    $email = $_POST['email'] ?? null;
    $redirect_to = $_POST['redirect-to'] ?? null;

    try {
        $tags = validateAndSplitTags($_POST['tags'] ?? "");
    } catch (Exception $e) {
        header("HTTP/1.1 400 Bad Request");
        echo $e->getMessage();
        return;
    }

    if (!filter_var($email, FILTER_VALIDATE_EMAIL) || !filter_var($redirect_to, FILTER_VALIDATE_URL)) {
        header("HTTP/1.1 400 Bad Request");
        return;
    }

    $contact = getContactByEmail($email);
    if (!$contact) {
        $contact = addContact($email);
    }

    if (!$contact) {
        header("HTTP/1.1 500 Internal Server Error");
        echo "Could not get or add contact\n";
        return;
    }

    // Verify that all tags exist, then assign them
    $tagIds = [];
    foreach ($tags as $tagName) {
        $tag = getTagByName($tagName);
        if ($tag) {
            $tagIds[] = $tag->id;
        }
    }
    if (count($tagIds) != count($tags)) {
        header("HTTP/1.1 404 Not Found");
        echo "Could not find all tags\n";
        return;
    }
    foreach ($tagIds as $tagId) {
        $response = assignTagToContact($contact->id, $tagId);
        if (!$response) {
            header("HTTP/1.1 500 Internal Server Error");
            echo "Could not assign tag to contact\n";
            return;
        }
    }

    header("HTTP/1.1 303 See Other");
    header("Location: $redirect_to");
}

function diagnose() {
    echo "<html>\n<head>\n<title>Environment check</title>\n</head>\n<body>\n<pre>\n";
    echo "API_BASE_URL: " . API_BASE_URL . "\n";
    if (strlen(API_KEY) != 64) {
        echo "API_KEY: (invalid: has " . strlen(API_KEY) . " characters)\n";
    } else {
        echo "API_KEY: (OK)\n";
    }
    if (function_exists('curl_init')) {
        echo "curl_init is defined\n";
    } else {
        echo "curl_init is not defined\n";
    }
    echo "\n</pre>\n</body>\n</html>\n";
}
