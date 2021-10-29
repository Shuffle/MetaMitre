echo "Ensuring deploy is running with project meta-mitre"
gcloud config set project meta-mitre

echo "Deploying function with name get_mitre_result"
gcloud functions deploy get_mitre_result \
	--entry-point=get_mitre_result \
	--region=europe-west1 \
	--runtime=python37 \
	--verbosity=debug \
	--memory=1024MB \
	--set-env-vars SHUFFLE_APIKEY="2&&xml%HQQ883NlGfeK" \
	--source="./source" \
	--trigger-http \
	--allow-unauthenticated
