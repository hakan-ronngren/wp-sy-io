# wp-sy-io

This is an integration that allows me to put a form on WordPress that creates/updates a subscription with (already defined) tags through the [API](https://developer.systeme.io/reference/api).

Fields:

* `email`
* `tags` - preferably hidden, a comma-separated list
* `redirect-to` - what page to load after posting

## Deploy

Run `make stage` to prepare the `./staging` area, which will contain everything that should be copied to the production environment.

The `production-config.php` file will be incomplete. You may want to put the API token in place in the target environment rather than keeping a copy in your development environment.
Just remember not to overwrite it.

If the `add-subscriber.php` finds a misconfiguration, it will redirect a POST to a GET request that runs diagnose mode. Hence a good way of testing it is to re-submit your test subscription.
