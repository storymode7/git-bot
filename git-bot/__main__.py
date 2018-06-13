import os
import aiohttp

from aiohttp import web

from gidgethub import routing, sansio
from gidgethub import aiohttp as gh_aiohttp

router = routing.Router()

@router.register("pull_request", action="closed")
async def issue_opened_event(event, gh, *args, **kwargs):
    """ Greet author of issue, whenever it is opened """
    if event.data["pull_request"]["merged"] == "true":
        url = event.data["pull_request"]["html_url"]
        author = event.data["pull_request"]["user"]["login"]
        message = f"Hey @{author}, Thanks for Pull Request! :)"
        print("Inside merged, and posting data")
        await gh.post(url, data={"body":message})
    else:
        print("Couldn't return, merge was: {event.data['pull_request']['merged']}")
        return

async def main(request):
    # read the GitHub webhook payload
    body = await request.read()

    # add authentication token and webhook secret
    secret = os.environ.get("GH_SECRET")
    oauth_token = os.environ.get("GH_AUTH")

    # a representation of github webhook event
    event = sansio.Event.from_http(request.headers, body, secret=secret)

    # pay attention to the username used 
    async with aiohttp.ClientSession() as session:
        gh = gh_aiohttp.GitHubAPI(session, "storymode7", oauth_token=oauth_token)

        # call appropriate callback for the event
        await router.dispatch(event, gh)

    # return "Success" response
    return web.Response(status=200)

if __name__ == "__main__":
    app = web.Application()
    app.router.add_post("/", main)
    port = os.environ.get("PORT")
    if port is not None:
        port = int(port)

    web.run_app(app, port=port)


