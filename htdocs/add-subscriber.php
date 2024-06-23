<?php
$api_base_url = getenv('SYSTEME_IO_BASE_URL') ?: 'https://api.systeme.io';
$api_key = getenv('SYSTEME_IO_API_KEY');

// For convenience, we can check that the environment is complete using a GET request
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    if (!$api_key) {
        echo "SYSTEME_IO_API_KEY not set\n";
    } else {
        echo "SYSTEME_IO_BASE_URL = " . $api_base_url . ", SYSTEME_IO_API_KEY is set\n";
    }
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = $_POST['email'] ?? null;
    $redirect_to = $_POST['redirect-to'] ?? null;
    if (!filter_var($redirect_to, FILTER_VALIDATE_URL)) {
        echo "Invalid redirect-to\n";
    } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        echo "Invalid email\n";
    } else {
        $url = $api_base_url . '/api/contacts';
        $data = ['email' => $email];
        $data_string = json_encode($data);
        $ch = curl_init($url);
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
        curl_close($ch);
        if ($result) {
            $response = json_decode($result);
            $id = $response->id ?? null;
            if (curl_getinfo($ch, CURLINFO_HTTP_CODE) == 201) {
                header("HTTP/1.1 303 See Other");
                header("Location: $redirect_to");
                echo "Subscriber added with id $id\n";
            } else {
                # TODO: Do something nice
                echo "Error: email already exists\n";
            }
        } else {
            echo '{"error":"' . curl_error($ch) . "\"}\n";
        }
    }
}
