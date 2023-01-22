import json
import requests
import time

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

#request data and parse out the proposals
r = requests.post(url, json={'query': proposals_query}).text
r = json.loads(r)["data"]["proposals"]

# create a list of all proposal numbers
proposals = []
for proposal in r:
    proposals.append(str(proposal["id"]))

master = {}

# for each proposal, construct multiple queries to gather all of the votes.
# note that the skip feature of the votes query has a maximum value of 5000, while some proposals are currently getting >8k votes.
# in order to account for this limiting factor, I run 2 loops: the first descending, the second ascending, and then remove duplicates.
for proposal in proposals:
    #print(proposal)
    time.sleep(1)
    voters = []
    # in this first loop, I gather 5,000 votes in descending order
    for i in range(0,5000,1000):
        vote_query = ("""query Votes {
        votes (
            first: 1000
            skip: """) + str(i) + ("""
            where: {
                proposal:""") + ' "' + str(proposal) + '"' + ("""
            }
            orderBy: "created",
            orderDirection: desc
        ) {
            voter
        }
        }""")

        #make request for 1000 votes at a time
        r = requests.post(url, json={'query': vote_query})
        r = json.loads(r.text)["data"]["votes"]

        #add results to ongoing list
        for vote in r:
            voters.append(str(vote["voter"]))

    #wait to avoid overloading the endpoint
    time.sleep(1)

    #now make 5 more calls, this time in ascending order
    for i in range(0,5000,1000):
        vote_query = ("""query Votes {
        votes (
            first: 1000
            skip: """) + str(i) + ("""
            where: {
                proposal:""") + ' "' + str(proposal) + '"' + ("""
            }
            orderBy: "created",
            orderDirection: asc
        ) {
            voter
        }
        }""")

        #make request for 1000 votes
        r = requests.post(url, json={'query': vote_query}).text
        r = json.loads(r)["data"]["votes"]

        #add more votes to the list
        for vote in r:
            voters.append(str(vote["voter"]))

    #remove the duplicates using list = list(dict(list)
    voters = list(dict.fromkeys(voters))

    #print the proposal and the total number of votes it got
    print(proposal, len(voters))

    #for each voter in this proposal, tally their total votes in the master dict
    for voter in voters:
        master[voter] = master.get(voter, 0) + 1

    #print the master dict to a file w format: {wallet address: total votes}
    with open("output.txt", 'w') as output:
        output.write(json.dumps(master))

output.close

#print the current number of closed proposals 
print("total proposals counted: ", len(proposals))