<?php
// https://developer.systeme.io/reference/api

$api_base_url = getenv('SYSTEME_IO_BASE_URL') ?: 'https://api.systeme.io';
$api_key = getenv('SYSTEME_IO_API_KEY') ?: null;

if (!$api_base_url) {
    echo "SYSTEME_IO_BASE_URL not set\n";
} elseif (!$api_key) {
    echo "SYSTEME_IO_API_KEY not set\n";
} else {
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        handlePost($api_base_url, $api_key);
    } elseif ($_SERVER['REQUEST_METHOD'] === 'GET') {
        echo "SYSTEME_IO_BASE_URL: $api_base_url\n";
        if ($api_key) {
            echo "SYSTEME_IO_API_KEY: (OK)\n";
        } else {
            echo "SYSTEME_IO_API_KEY: (undefined)\n";
        }
    } else {
        header("HTTP/1.1 405 Method Not Allowed");
    }
}

function postToAPI($url, $api_key, $data) {
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
        'X-Api-Key: ' . $api_key,
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

function getFromAPI($url, $api_key) {
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'X-Api-Key: ' . $api_key,
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

function getContactByEmail($api_base_url, $api_key, $email) {
    $path = '/api/contacts';
    $url = $api_base_url . $path;
    [$status, $response] = getFromAPI("$url?email=$email", $api_key);
    if ($status == 200) {
        return $response->items[0] ?? null;
    } else {
        return null;
    }
}

function addContact($api_base_url, $api_key, $email) {
    $path = '/api/contacts';
    $url = $api_base_url . $path;
    $data = ['email' => $email];
    [$status, $response] = postToAPI($url, $api_key, $data);
    if ($status == 201) {
        return $response ?? null;
    } else {
        return null;
    }
}

function getTagByName($api_base_url, $api_key, $tag) {
    $path = '/api/tags';
    $url = $api_base_url . $path;
    [$status, $response] = getFromAPI("$url?query=$tag", $api_key);
    if ($status == 200) {
        return $response->items[0] ?? null;
    } else {
        return null;
    }
}

function assignTagToContact($api_base_url, $api_key, $contact_id, $tag_id) {
    $path = "/api/contacts/$contact_id/tags";
    $url = $api_base_url . $path;
    $data = ['tagId' => $tag_id];
    [$status] = postToAPI($url, $api_key, $data);
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

function handlePost($api_base_url, $api_key) {
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

    $contact = getContactByEmail($api_base_url, $api_key, $email);
    if (!$contact) {
        $contact = addContact($api_base_url, $api_key, $email);
    }

    if (!$contact) {
        header("HTTP/1.1 500 Internal Server Error");
        echo "Could not get or add contact\n";
        return;
    }

    // Verify that all tags exist, then assign them
    $tagIds = [];
    foreach ($tags as $tagName) {
        $tag = getTagByName($api_base_url, $api_key, $tagName);
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
        $response = assignTagToContact($api_base_url, $api_key, $contact->id, $tagId);
        if (!$response) {
            header("HTTP/1.1 500 Internal Server Error");
            echo "Could not assign tag to contact\n";
            return;
        }
    }

    header("HTTP/1.1 303 See Other");
    header("Location: $redirect_to");
}
