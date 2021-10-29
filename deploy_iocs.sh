echo "Ensuring deploy is running with project meta-mitre"
gcloud config set project meta-mitre

echo "Deploying function with name get_mitre_result"
gcloud functions deploy get_ioc_result \
	--entry-point=get_ioc_result \
	--region=europe-west2 \
	--runtime=python37 \
	--verbosity=debug \
	--memory=512MB \
	--set-env-vars SHUFFLE_APIKEY="2&&xml%HQQ883NlGfeK" \
	--source="./functions" \
	--trigger-http \
	--allow-unauthenticated
