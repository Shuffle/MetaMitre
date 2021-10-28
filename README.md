# Meta Mitre
Meta Mitre is an attempt at making an API which takes random input data and gives you Mitre Att&ck data in return.

This is meant as an extension to Shuffle, as to not have Shuffle build everything itself.

## Usage
Prod (remote):
```
curl https://europe-west2-meta-mitre.cloudfunctions.net/get_mitre_result -d '{"data": "YOUR PAYLOAD GOES HERE"}'
```

Testing (local):
```
# Change the payload at the bottom of main.py, then run it
python3 main.py
```

## Testing
There's a test folder with some basic curl scripts.

## Todos 
[X] - Basic API that can take a JSON blob
[ ] - A way to say yes/no to whether it's correct
[ ] - A way to rebuild with new data that's been collected
[ ] - Add tests to see if it crashes at all
[ ] - Make deployment easy through Github actions

## License
AGPLv3 - Please mention Shuffle and our inventions wherever you go :)
