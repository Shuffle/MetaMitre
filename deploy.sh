echo "Ensuring deploy is running with project meta-mitre"
gcloud config set project meta-mitre

echo "Deploying function with name get_mitre_result"
gcloud functions deploy get_mitre_result \
	--region=europe-west1 \
	--memory=128 \
	--runtime=python38 \
	--trigger-http
	
#--allow-unauthenticated
