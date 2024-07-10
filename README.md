# wp-sy-io

This is a limited but light-weight integration that allows you to put a form on WordPress that creates/updates a subscription with (already defined) tags through the [systeme.io API](https://developer.systeme.io/reference/api?sa=sa0172651241869e6c56e81cf29bafddb07877696f). There is actually not much WordPress about it, but it is written in the PHP language so it can be dropped right into a WordPress installation. The result you'll get is a simple funnel with a landing page that collects an email address and assigns tags. You can then create an automation in [systeme.io](https://systeme.io/?sa=sa0172651241869e6c56e81cf29bafddb07877696f) that reacts to the user being assigned a tag and proceeds from there.

For other ways of integrating with [systeme.io](https://systeme.io/?sa=sa0172651241869e6c56e81cf29bafddb07877696f), [search for wordpress](https://help.systeme.io/search?query=wordpress&sa=sa0172651241869e6c56e81cf29bafddb07877696f) on their help site.

## Fields

* `email`
* `tags` - preferably hidden, a comma-separated list
* `redirect-to` - what page to load after posting

## Deploy

Run `make staging` to prepare the `./staging` area, which will contain everything that should be copied to the production environment. In other words, you should not copy everything in `./htdocs` to your production environment.

The `systeme-io-config.php` file will be incomplete. You may want to put the API token in the target environment rather than keeping a copy in your development environment. If you delete your local file, it won't be put there again until you wipe and recreate the staging directory as a whole. Deleting your local file is a good way of preventing yourself from overwriting the target file.

Put it in a subfolder named `.private`, where there is a `.htaccess` file that just says `Deny from all`.

If the `add-systeme-io-contact.php` script finds a misconfiguration, it will redirect to a request that prints diagnostic output. (Nothing sensitive there.) This enables you to easily test after deployment by just re-submitting a subscription through your form.

## Debug

You can read the API mock request log like this:

```bash
make list-mock-requests
```
