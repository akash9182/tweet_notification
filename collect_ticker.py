import twint

# Configure
c = twint.Config()
c.Username = "MrZackMorris"
c.Search = "$CEI"
c.Output = "tweets.csv"
c.Store_csv = True

twint.run.Search(c)