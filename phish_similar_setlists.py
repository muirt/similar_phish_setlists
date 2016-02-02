from bs4 import BeautifulSoup
import os

#set this to True to download the html.  No need to download multiple times
downloadYears = False

#the second number is not included in the result
validYears = range(1983,2017)


#download html of a full year of setlists
if downloadYears:
    for year in validYears:
        yearURL = "http://phish.net/setlists/{0}.html".format(year)
        os.system("curl {0} > {1}.html".format(yearURL, year))

class Setlist:
	def __init__(self):
		self.date = ""
		self.songlist = []

class Comparison:
    def __init__(self, date1, date2):
        self.date1 = date1
        self.date2 = date2
        self.matches = 0

#the actual comparison of two setlists
def compare(setlist1, setlist2):
    #make an object to store the result
    comparison = Comparison(setlist1.date, setlist2.date)
    #look for every song in show 1 in show 2's setlist, accumulate matches
    for song in setlist1.songlist:
        if song in setlist2.songlist:
            comparison.matches += 1
    return comparison

#rough estimate.  Far less effort than implementing all the rules of a calendar
def total_days(date):
    date_elements = date.split("-")
    return int(date_elements[0]) * 365 + int(date_elements[1]) * 30 + int(date_elements[2])

def date_gap(comparison):
    date1 = comparison.date1
    date2 = comparison.date2
    return total_days(date2) - total_days(date1)


dateDict = {}
all_setlists = []
yearRange = range(1983,2016)


#open each year's html, and use beautiful soup to extract the setlist of every show
for year in yearRange:
    #open the file
    soup = BeautifulSoup(open('{0}.html'.format(str(year))),"lxml")
    #find all div tags with the class "setlist"
    dateDivs = soup.find_all('div', attrs={'class': 'setlist'})
    #for each of those divs, which maps to a single set
    for div in dateDivs:
        #make a new setlist object
        slist = Setlist()
        #the first link inside the first header inside the div has a url with the date of the show
        link = div.h2.a
        if link.has_attr('href'):
            #isolate just the date from the url
            slist.date = str(link['href']).split("=")[1]
        #create a soup just from this div
        song_groups_soup = BeautifulSoup(str(div), "lxml")
        #find all <p> tags
        song_groups = song_groups_soup.find_all('p')
        #this is a list of links to songs
        for group in song_groups:
            #make a soup of this song list
            songs_soup = BeautifulSoup(str(group), "lxml")
            #find all links
            song_links = songs_soup.find_all('a')
            #each link has a song name in it
            for song_link in song_links:
                #dont include links for teases
                if "?teaseid=" not in str(song_link):
                    #trim the url to just the song
                    song_name = song_link['href'].replace("http://phish.net/song/", "")
                    #only add the song name to the list if its not already there
                    if song_name not in slist.songlist:
                        slist.songlist.append(song_name)
        #add the setlist to the list of all setlists ever
        all_setlists.append(slist)

#at this point all_setlists holds just that, all setlists, ready to be compared



#if we compared every show to every other show, that would duplicate every comparison.
#to avoid this, only compare show1 to shows that are further down the list than show 1.
#the first show gets compared to every other show, the third to last show only gets compared to 2 shows.


show_count = len(all_setlists)

#if there are > 2000 shows, this list ends up holding > 3,000,000 objects
all_comparisons = []

#index is the number of loops so far, show1 is all_setlists[index]
for (index, show1) in enumerate(all_setlists):
    #only compare to shows with a larger index
    for show2 in all_setlists[index+1:show_count]:
        #run the comparison and add the result to the list of all comparisons
        all_comparisons.append(compare(show1,show2))

#sort the comparisons by the number of matches
sorted_comparison_matches = sorted(all_comparisons, key=lambda x: x.matches, reverse=True)
#print out the top 10
for (index, comparison) in enumerate(sorted_comparison_matches):
    print "{0} and {1} had {2} matches".format(comparison.date1, comparison.date2, comparison.matches)
    if index == 9:
        break

#sort the top 500 of the previous sorted list, but in descending order of days between the compared shows
sorted_comparison_matches_biggest_gap = sorted(sorted_comparison_matches[0:500], key=lambda x: date_gap(x), reverse=True)

#print the top 10
for (index, comparison) in enumerate(sorted_comparison_matches_biggest_gap):
    print "{0} and {1} had {2} days apart and {3} matches".format(comparison.date1, comparison.date2, date_gap(comparison), comparison.matches)
    if index == 9:
        break