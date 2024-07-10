# wp-sy-io

This is a limited but lightweight integration that allows you to put a form on WordPress that creates/updates a subscription with (already defined) tags through the [systeme.io API](https://developer.systeme.io/reference/api?sa=sa0172651241869e6c56e81cf29bafddb07877696f). There is actually not much WordPress about it, but it is written in the PHP language so it can be dropped right into a WordPress installation. The result you'll get is a simple funnel with a landing page that collects an email address and assigns tags. You can then create an Automation in [systeme.io](https://systeme.io/?sa=sa0172651241869e6c56e81cf29bafddb07877696f) that reacts to the user being assigned a tag and proceeds from there.

For other ways of integrating with [systeme.io](https://systeme.io/?sa=sa0172651241869e6c56e81cf29bafddb07877696f), [search for wordpress](https://help.systeme.io/search?query=wordpress&sa=sa0172651241869e6c56e81cf29bafddb07877696f) on their help site.

## Fields

* `email`
* `first_name`
* `tags` - preferably hidden, a comma-separated list
* `redirect-to` - what page to load after posting

## Deploy

Deployment is done by a GitHub workflow.

The `systeme-io-config.php` file goes into a subfolder named `.private`, in which there should be a `.htaccess` file that just says `Deny from all`.

If the `add-systeme-io-contact.php` script finds a misconfiguration, it will redirect to a request that prints diagnostic output. (Nothing sensitive there.) This enables you to easily test after deployment by just re-submitting a subscription through your form.

## Debug

You can read the API mock request log like this:

```bash
make list-mock-requests
```
