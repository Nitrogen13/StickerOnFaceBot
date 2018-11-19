# StickerToFaceBot
To create a lambda package, install libraries in `./lib`:

`pip3 install -r requirements.txt -t lib`

And package everything as zip:

`zip -9 -r package lib lambda_function.py key.txt src`

Upload package.zip to AWS lambda.
