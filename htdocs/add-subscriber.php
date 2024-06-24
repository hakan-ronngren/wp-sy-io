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
            echo "SYSTEME_IO_API_KEY: (set)\n";
        } else {
            echo "SYSTEME_IO_API_KEY: (not set)\n";
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

function handlePost($api_base_url, $api_key) {
    $email = $_POST['email'] ?? null;
    $redirect_to = $_POST['redirect-to'] ?? null;
    if (!filter_var($email, FILTER_VALIDATE_EMAIL) || !filter_var($redirect_to, FILTER_VALIDATE_URL)) {
        header("HTTP/1.1 400 Bad Request");
    } else {
        $path = '/api/contacts';
        $url = $api_base_url . $path;
        $data = ['email' => $email];
        [$status, $response] = postToAPI($url, $api_key, $data);

        if (!$status) {
            echo "POST $path did not respond; $response\n";
        } elseif ($status == 201) {
            $id = $response->id ?? null;
            header("HTTP/1.1 303 See Other");
            header("Location: $redirect_to");
            echo "Contact added with id $id\n";
        } elseif ($status == 422) {
            [$status, $response] = getFromAPI("$url?email=$email", $api_key);
            $response_str = json_encode($response);
            if ($status == 200) {
                if (count($response->data) != 1) {
                    echo "Got" . count($response->data) . "contacts, expected 1\n";
                } else {
                    $id = $response->data[0]->id ?? null;
                    if ($id) {
                        header("HTTP/1.1 303 See Other");
                        header("Location: $redirect_to");
                        echo "Contact already exists with id $id\n";
                    } else {
                        echo "Contact already exists but id not found\n";
                    }
                }
            } else {
                echo "POST $path returned 422, GET $path returned $status, response = '$response_str'\n";
            }
        } else {
            echo "POST $path returned $status, response = '$response_str'\n";
        }
    }
}
