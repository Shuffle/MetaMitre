# Should fail
curl -XPOST https://europe-west1-meta-mitre.cloudfunctions.net/get_mitre_result -d "hello this is some text"

# Should succeed with basic auth here 
curl -XPOST https://europe-west1-meta-mitre.cloudfunctions.net/get_mitre_result -H "Authorization: 2&&xml%HQQ883NlGfeK" -d "hello this is some text"
