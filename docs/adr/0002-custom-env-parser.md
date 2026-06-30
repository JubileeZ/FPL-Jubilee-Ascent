# Custom .env parser

We decided to implement a custom parser in the standard library to load environment variables from `.env` files rather than adding `python-dotenv`. This keeps core dependencies to a minimum, following the ponytail design principle ("no new dependency if it can be avoided").
