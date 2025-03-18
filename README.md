# fast-vue
A minimal sample to demonstrate using FastAPI and Vue in a single repo using a dual [devcontainers](https://containers.dev) setup for local development and a [multi stage Dockerfile](https://docs.docker.com/build/building/multi-stage/) for building a "production" container with both the Vue-UI and the FastAPI-API.

# Links
* https://code.visualstudio.com/remote/advancedcontainers/connect-multiple-containers
* https://fastapi.tiangolo.com/tutorial/first-steps/
* https://vuejs.org/guide/quick-start

# Getting started
## Local development with devcontainers

> Following instructions relate to VS Code, IntelliJ and other IDEs should work accordingly. 

> Prerequisites are working local container solution and the dev containers extension installed.

The [.devcontainer-Folder](./devcontainer/) in this repo contains two `devcontainer.json` definitions using a common [docker-compose.yaml](./.devcontainer/docker-compose.yaml) file.

1. Clone the repo, open it in VS Code.
1. Start `Reopen in container` command (e.g. from the blue remote icon in the very bottom left corner of VS Code). As there are two devcontainer definitions in this repo, you will be presented with the option to either open `py-api` or `node-app`. Choose `py-api`.
1. Once the devcontainer loads, open a terminal and start the fastapi server with dev watcher:
   ```sh
   ./run-dev.sh
   ```
   (`run-dev.sh` is a convenience script in both vue-appp and py-api, so that you do not need to remember the vue and fastapi commands)
1. Open another VS Code window.
1. Start `Reopen in container` again, choose `node-app`. This will **not** start another instance of the containers in our [docker-compose file](./.devcontainer/docker-compose.yaml), but instead will attach our VS Code to the already `py-api` running container that we started from the other VS Code window. This way the two containers can interact with each other in their private network.
1. Once the devcontainer loads, open a terminal and start the vue server with dev watcher:
   ```sh
   ./run-dev.sh
   ```
Now you can work in both the fastapi and vue part, both with file watchers set up, so that any change is immmediately picked up by the respective servers.

The vue app (node app) has a proxy set up (defined in [vite.config.ts](./node-app/vite.config.ts)), which forwards all requests that cannot be handled by the vue app's routing to `http://py-api:8000`, which is exactly where our fastapi app is listening in the `py-api` dev container. This way we can use the same relative paths to the api that can be used in the production container.

## Production container

The production container is built using the multi stage build [Dockerfile](./Dockerfile) in this repo. This Dockerfile contains one stage to build the node app, one for the fastapi app and a final (minimal) stage which produces the final container image. This final image gets the build results of both the fastapi and the vue app. During runtime, the container then starts a uvicorn server hosting the fastapi api implementation and serving the vue app as static files in the root path.

To build and run:

```sh
docker buildx build -t fast-vue:latest .
docker container run -p 80:80 fast-vue    
```

Then the app should be available at "http://localhost:80"

# Routing

One special setting is the handling of non-API routes in the fastapi app. This needs to make sure that a route like "/about" or "/home" will be handled by the Vue.js app in "index.html". By default, if the Vue.js app is simply stored in a static files folder and served using the [StaticFiles](https://fastapi.tiangolo.com/tutorial/static-files/) class, then all routes other than our "/api" routes will be treated as requests for static files of that name. E.g. for "/about", the static file hosting will try to find an "/about/index.html" file, which does not exist - accordingly, it will produce a 404. Thus we need to handle those 404s by simply redirecting them to our "index.html" again, which contains our Vue.js app, that in turn will correctly handle these routes:

```python
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    return FileResponse(static_dir / "index.html")
```
