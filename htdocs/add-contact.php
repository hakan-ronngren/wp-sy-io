<?php
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0, Cache-Control: post-check=0, pre-check=0');
header('Pragma: no-cache');

class InputException extends Exception {}
class InternalServerError extends Exception {}
class APICallException extends Exception {}

# TODO: Save data locally if a POST request fails

if (file_exists('production-config.php')) {
    require_once 'production-config.php';
} else {
    define('API_BASE_URL', getenv('API_BASE_URL') ?: 'https://api.systeme.io');
    define('API_KEY', getenv('API_KEY') ?: null);
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!API_BASE_URL || !API_KEY) {
        # Misconfigured; redirect to a GET request to self, which will run a diagnose
        header("HTTP/1.1 303");
        header("Location: /add-subscriber.php");
    } else {
        # The plan is to redirect the visitor different pages depending on whether the request was successful or not
        # but for now we just return a 400 or 500 error unless the request is successful.
        try {
            handlePost();
        } catch (InputException $e) {
            header("HTTP/1.1 400 Bad Request");
            echo $e->getMessage();
        } catch (InternalServerError $e) {
            header("HTTP/1.1 500 Internal Server Error");
            echo $e->getMessage();
        } catch (APICallException $e) {
            header("HTTP/1.1 500 Internal Server Error");
            echo $e->getMessage();
        } catch (Exception $e) {
            header("HTTP/1.1 500 Internal Server Error");
            echo $e->getMessage();
        }
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
        throw new InternalServerError('curl_init failed');
    }
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'POST');
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data_string);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json',
        'Content-Length: ' . strlen($data_string),
        'X-API-Key: ' . API_KEY,
    ]);
    $result = curl_exec($ch);
    if ($result === false) {
        $error = curl_error($ch);
        curl_close($ch);
        throw new APICallException('curl_exec failed: ' . $error);
    }
    $status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    return [$status, json_decode($result)];
}

function patchToAPI($url, $data) {
    $data_string = json_encode($data);
    $ch = curl_init($url);
    if ($ch === false) {
        throw new InternalServerError('curl_init failed');
    }
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'PATCH');
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data_string);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/merge-patch+json',
        'Content-Length: ' . strlen($data_string),
        'X-API-Key: ' . API_KEY,
    ]);
    $result = curl_exec($ch);
    if ($result === false) {
        $error = curl_error($ch);
        curl_close($ch);
        throw new APICallException('curl_exec failed: ' . $error);
    }
    $status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    return [$status, json_decode($result)];
}

function getFromAPI($url) {
    $ch = curl_init($url);
    if ($ch === false) {
        throw new InternalServerError('curl_init failed');
    }
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'X-API-Key: ' . API_KEY,
    ]);
    $result = curl_exec($ch);
    if ($result === false) {
        $error = curl_error($ch);
        curl_close($ch);
        throw new APICallException('curl_exec failed: ' . $error);
    }
    $status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    return [$status, json_decode($result)];
}

// Get a contact by email, or null if not found
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

// Add a contact. Return the contact or null if not successful
function addContact($email, $firstName) {
    $path = '/api/contacts';
    $url = API_BASE_URL . $path;
    $data = ['email' => $email, 'fields' => []];
    if ($firstName) {
        $data['fields'][] = ['slug' => 'first_name', 'value' => $firstName];
    }
    [$status, $response] = postToAPI($url, $data);
    if ($status == 201) {
        return $response;
    } else {
        return null;
    }
}

// Get a tag by name, or null if not found
function getTagByName($tag) {
    $path = '/api/tags';
    $url = API_BASE_URL . $path;
    [$status, $response] = getFromAPI("$url?query=$tag");
    if ($status == 200) {
        return $response->items[0];
    } else {
        return null;
    }
}

// Assign a tag to a contact. Return true if successful
function assignTagToContact($contact_id, $tag_id) {
    $path = "/api/contacts/$contact_id/tags";
    $url = API_BASE_URL . $path;
    $data = ['tagId' => $tag_id];
    [$status] = postToAPI($url, $data);
    # 204 No Content (there is no response body)
    return $status == 204;
}

// Validate tags string and return an array of valid tags
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
            throw new InputException("Invalid tag: $tag");
        }
    }

    return $validTags;
}

function handlePost() {
    # Required parameters
    $email = $_POST['email'] ?? null;
    $redirectTo = $_POST['redirect-to'] ?? null;
    # Optional parameters
    $firstName = $_POST['first_name'] ?? null;

    $tags = validateAndSplitTags($_POST['tags'] ?? "");

    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        throw new InputException("Invalid email");
    }

    if (!filter_var($redirectTo, FILTER_VALIDATE_URL)) {
        throw new InputException("Invalid redirect-to");
    }

    // Replace all single quotes in $firstName with apostrophes to prevent SQL injection.
    // Then validate that $firstName is a string of international characters, spaces, hyphens, and some cultural characters.
    $firstName = str_replace("'", "’", $firstName);
    if (!empty($firstName) && !preg_match("/^[\p{L}\s.’\-·,]+$/u", $firstName)) {
        throw new InputException("Invalid first_name");
    }

    $contact = getContactByEmail($email);
    if ($contact) {
        $storedFirstName = null;
        foreach ($contact->fields as $field) {
            if ($field->slug == 'first_name') {
                $storedFirstName = $field->value;
                break;
            }
        }

        if ($firstName && $storedFirstName != $firstName) {
            $path = "/api/contacts/$contact->id";
            $url = API_BASE_URL . $path;
            $data = ['fields' => [['slug' => 'first_name', 'value' => $firstName]]];
            [$status, $contact] = patchToAPI($url, $data);
            if ($status != 200) {
                throw new APICallException("Could not update contact");
            }
        }
    } else {
        $contact = addContact($email, $firstName);
    }

    // By now the contact should be either found or added
    if (!$contact) {
        throw new APICallException("Could not get or add contact");
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
        throw new InputException("Could not find all tags");
    }
    foreach ($tagIds as $tagId) {
        $response = assignTagToContact($contact->id, $tagId);
        if (!$response) {
            throw new APICallException("Could not assign tag to contact");
        }
    }

    header("HTTP/1.1 303 See Other");
    header("Location: $redirectTo");
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
