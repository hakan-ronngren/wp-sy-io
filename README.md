# wp-sy-io

This is a limited but light-weight integration that allows me to put a form on WordPress that creates/updates a subscription with (already defined) tags through the [systeme.io API](https://developer.systeme.io/reference/api).

For a full integration, see https://help.systeme.io/article/1592-how-to-integrate-a-form-or-a-popup-on-wordpress

## Fields

* `email`
* `tags` - preferably hidden, a comma-separated list
* `redirect-to` - what page to load after posting

## Deploy

Run `make staging` to prepare the `./staging` area, which will contain everything that should be copied to the production environment.

The `production-config.php` file will be incomplete. You may want to put the API token in place in the target environment rather than keeping a copy in your development environment. If you delete it, it won't be put there again until you wipe and recreate the staging directory as a whole. This is a good way of preventing yourself from overwriting the target file.

If the `add-subscriber.php` finds a misconfiguration, it will redirect a POST to a GET request that runs diagnose mode. Hence a good way of testing it after deployment is to re-submit your test subscription.
