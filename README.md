# Alfred Kibana

Quickly navigate to Datadog Saved Views in [Alfred][alfred].

![][sample]

### Warning - No official API
Datadog has no official API to list saved views, so this relies on your web auth token
and uses undocumented APIs.

## Setup and Usage
Setup and Usage

You will need to get an auth token and your Datadog shard out of your cookies.
* Open an incognito window and login to Datadog.
* Open Developer Tools and go to cookies
* You are looking for two cookies. `DD-PSHARD` and `dogweb`.
* Copy the contents of `DD-PSHARD` and run `ddlogsetshard <number>` ie... `ddlogsetshard 123`
* Copy the contents of `dogweb` and run `ddlogsetauth <auth token>`
* Set your Datadog url: `ddlogseturl app.datadoghq.com` or `ddlogseturl app.datadoghq.eu`

## TODOs
* Initial release.

# Thanks, License, Copyright

- The [Alfred-Workflow][alfred-workflow] library is used heavily, and it's wonderful documentation was key in building the plugin.
- The Datadog icon, care of Datadog.

All other code/media are released under the [MIT Licence][license].

[alfred]: http://www.alfredapp.com/
[alfred-workflow]: http://www.deanishe.net/alfred-workflow/
[license]: src/LICENSE.txt
[sample]: https://raw.github.com/lukewaite/alfred-kibana/master/docs/sample.png