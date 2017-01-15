# Job Offers Data Mining

EPFL — Bachelor, Semester 5 (Semester Project)

### Graph
<img src="https://github.com/MatteoGiorla/job-offers-data-mining/blob/master/img/graph.png">

### Histogram
<img src="https://github.com/MatteoGiorla/job-offers-data-mining/blob/master/img/histogram.png">

## How to use

To extract the skills from job offers and generate a graph simply run ```python main.py```.

### Prerequisites

First start by placing the files containing the job offers in the ```data/``` folder. Each job offer has to be in a separate JSON file containing at least 2 fields :

- ```"TranslatedText"``` : this field should contain the body of the job offer in english.
- ```"Category"``` : this field contains the category of the job offer. It has to be one of the following, be careful to have the exact same syntax :
	- ```"Administration, Consulting, HR"```
	- ```"Banking, Insurance"```
	- ```"Food, Tourism"```
	- ```"Biotechnology, Chemical and Pharma"```
	- ```"Construction, Architecture"```
	- ```"Electronics, Engineering"```
	- ```"Finance, Real Estate"```
	- ```"Graphics, Printing"```
	- ```"IT, Telecommunications"```
	- ```"Plant Engineering, Machines"```
	- ```"Marketing, Communication"```
	- ```"Medical"```
	- ```"Public Administration, Education, Social"```
	- ```"Logistics, Purchasing"```
	- ```"Sales, Customer Service"```
	- ```"Sport, Spa, Wellness"```
	- ```"Surveillance, Police, Rescue"```
	- ```"Vehicles, Transport"```

A typical job offer file in the ```data/``` folder could look like this : 
```json
{
	"Category": "Administration, Consulting, HR",
	"TranslatedText": "English job offer text"
}
```

### Outputs

**Graph and histogram :**
To visualize the results, you just need to open ```index.html```, located in the ```graph/``` folder. If you use it locally, be careful to run a local server to be able to see the content.

Graph uses the *sigma.js* library (https://github.com/jacomyal/sigma.js)

Histogram uses the *d3.js* library (https://github.com/d3/d3)

**JSON files :**
New fields are created in the JSON files to store the results. More particularly 3 new fields contain the detected skills of the job offer : ```"Skills"```, ```"GeneralQualities"``` and ```"Diploma"```.  These fields can easily be accessed.
