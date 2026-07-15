# PMHelper Edu — web frontend

The Angular frontend for PMHelper Edu (`pmhelper-edu-web`), generated with
[Angular CLI](https://github.com/angular/angular-cli) 18.2.9 and styled with
Tailwind.

It is a **client for the FastAPI backend** — it calls `/api/web/*` and does no
analysis of its own. Start the API before using the app, or every request fails:

```bash
# from the repo root, in a separate terminal
uvicorn pmhelper.server.main:app --reload      # http://localhost:8000
```

In production the same FastAPI app serves the built bundle, so the frontend and
API share an origin.

## Development server

```bash
npm install
npm start          # ng serve -> http://localhost:4200
```

The app reloads automatically when you change a source file.

## Build

```bash
npm run build      # ng build
npm run watch      # rebuild on change (development configuration)
```

Artifacts are written to `dist/pmhelper-edu-web/`.

## Tests

```bash
npm test           # unit tests via Karma
npm run lint       # ng lint
```

### End-to-end (Cypress)

Cypress is **already installed and configured** (`cypress/`, `cypress.config.ts`) —
you don't need to add an e2e package:

```bash
npm run e2e        # cypress run  (headless)
npm run e2e:open   # cypress open (interactive)
```

Use those scripts, **not `ng e2e`** — there is no `e2e` target in `angular.json`,
so the Angular CLI can't run them.

## Code scaffolding

```bash
ng generate component component-name
# also: directive | pipe | service | class | guard | interface | enum | module
```

## Further help

`ng help`, or the
[Angular CLI Overview and Command Reference](https://angular.dev/tools/cli).
