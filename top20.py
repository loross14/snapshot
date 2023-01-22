import json
import requests
import operator

#url for connecting to snapshot API
url = "https://hub.snapshot.org/graphql"

#create query string for first 1000 aave proposals
proposals_query = """query Proposals {
  proposals (
    first: 1000,
    skip: 0,
    where: {
      space_in: ["aave.eth"],
      state: "closed"
    },
    orderBy: "created",
    orderDirection: desc
  ) {
    id
  }
}"""

#request data for total number of proposals
r = requests.post(url, json={'query': proposals_query}).text
total_proposals = len(json.loads(r)["data"]["proposals"])

#open up the output file and read the data into a dict
with open("output.txt", 'r') as results_file:
  data = json.load(results_file)

#close the file
results_file.close

#sort the data and grab the last 20 only (works for python 2.x)
sorted_data = sorted(data.items(), key=operator.itemgetter(1))[-20:]

#now print out the top 20 voters and their percentage participation rate
for element in reversed(sorted_data):
  print(element,  element[1]/float(total_proposals) * 100)