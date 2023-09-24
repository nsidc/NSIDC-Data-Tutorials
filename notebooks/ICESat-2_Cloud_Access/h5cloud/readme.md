## Running and scaling Python with [Coiled serverless functions](https://docs.coiled.io/user_guide/usage/functions/index.html).

This script contains the same code to read ATL10 data as the notebook, the one difference is that we are using a function decorator from Coiled that allows us to execute the function in the cloud with no modifications whatsoever. 

The only requirement for this workflow is to have an active account with Coiled and execute this from our terminal:

```bash
coiled login
```

This will open a browser tab to authenticate ourselves with their APIs 

> Note: If you would like to test his ask us to include you with Openscapes!


Our functions can be paralleliza, scaling the computation to hundreds of nodes if needed in the same way we could use Amazon lambda functions. Once we install and activate [`nsidc-tutorials`](../../binder/environment.yml) We can run the script with the following python command:

```bash
python workflow.py --bbox="-180, -90, 180, -60" --year=2023 --out="test-2023-local" --env=local

```

This will run the code locally. If we want to run the code in the cloud we'll 

```bash
python workflow.py --bbox="-180, -90, 180, -60" --year=2023 --out="test-2023-local" --env=cloud

```

The first time we execute this function, the provisioning will take a couple minutes and will sync our current Python environment with the cloud instances executing our code.
