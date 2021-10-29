# Should fail
curl -XPOST https://europe-west2-meta-mitre.cloudfunctions.net/get_ioc_result -d "hello this is some text"

# Should return failure because bad content-type
curl -XPOST https://europe-west2-meta-mitre.cloudfunctions.net/get_ioc_result -H "Authorization: 2&&xml%HQQ883NlGfeK" -d "THIS IS SOME DATA"

#curl -XPOST https://shaffuru.com/mitre -H "Content-Type: text/plain" -H "Authorization: 2&&xml%HQQ883NlGfeK" -d "THIS IS SOME DATA"

# Should succeed with basic auth here 
curl -XPOST https://europe-west2-meta-mitre.cloudfunctions.net/get_ioc_result -H "Content-Type: text/plain" -H "Authorization: 2&&xml%HQQ883NlGfeK" -d "THIS IS SOME google.com DATA1.2.3.4"

#curl -XPOST https://shaffuru.com/get_mitre_result -H "Content-Type: text/plain" -H "Authorization: 2&&xml%HQQ883NlGfeK" -d "THIS IS SOME DATA"
