import numpy as np
import xlrd
import csv
import matplotlib.pyplot as plt
from scipy.interpolate import spline
import time


# Initial values
MIN_DEPTH=3	# minimum water vailable in well(feets)
water_depth=10
MAX_WATER_DEPTH=900 # If max water depth crossed stoped tube wells digging
AVG_DEPTH=70	# open well avg water depth
YIELD_PER_WELL = 10		# 10 ltrs/sec
VILLAGE_AREA = 150000	#3 x 5 km
#START_YEAR = 1960
#END_YEAR = 2002
NUM_SEASONS = 3		# every season contains 4 months(Kharif:Jul-OCt, Rabi:Nov-Feb,Summer: Mar-Jun )
NUM_MONTHS = 4		# no of months per season
NUM_DAYS = 30
MM_TO_FEET = (0.1 / (2.54*12))
PERCOLATION = 1
POROSITY=30
well_depth=0
min_rainfall=10 #mm
MAX_RAINY_DAYS=15

farmar_list=[]
crop_list=[]
wells_list=[]	#basic wells data(well_id,farmar_id,depth,lat,long,start date,end date,HP,well type)
s_rainfall=[]	#season rainfall
m_rainfall=[]	#monthly rainfall
ww_data_list=[]
c_data_years=[]
c_data_wells=[]

m_wells_water = []	#monthly wise wells water depth
d_wells_water = []	#day wise wells water depth

no_working_well=[] #no of working wells
no_dry_well=[] 		#no of not working wells
time_period = []	#time , year+month+day wise (year+(month/100)+(day/100))

TUBE_WELLS_TECH=1980
TOTAL_WELLS=76 #Initial well count

with open('./chittoor1960-2002.csv') as rain:
	rain_reader = csv.DictReader(rain)
	for row in rain_reader:
		m_rainfall.append([row['State'],row['District'],int(row['Year']),float(row['Jan']),float(row['Feb']),float(row['Mar']),float(row['Apr']),float(row['May']),float(row['Jun']),float(row['Jul']),float(row['Aug']),float(row['Sep']),float(row['Oct']),float(row['Nov']),float(row['Dec'])])
		s_rainfall.append([int(row['Year']),float(row['Jul'])+float(row['Aug'])+float(row['Sep'])+float(row['Oct']),float(row['Nov'])+float(row['Dec'])+float(row['Jan'])+float(row['Feb']),float(row['Mar'])+float(row['Apr'])+float(row['May'])+float(row['Jun'])])
#print(row['first_name'], row['last_name'])
#print(m_rainfall)
START_YEAR=1960			#int(m_rainfall[0][2])	#start year in sheet
#print (START_YEAR)
END_YEAR=int(m_rainfall[len(m_rainfall)-1][2])	#end year in sheet
#print(END_YEAR)
#print(m_rainfall)
#print(s_rainfall)
with open('./well_data.csv') as wells:
	well_reader=csv.DictReader(wells)
	for row in well_reader:
		wells_list.append([row['well_id'],row['farmar_id'],row['depth'],row['lat'],row['long'],row['start_date'],row['end_date'],row['HP'],row['well_type'],row['Farm_extent'],row['State']])
	#print wells_list
with open('./crops.csv') as crop:
	crop_reader=csv.DictReader(crop)
	for row in crop_reader:
		crop_list.append([row['Crop_id'],row['Crop_Name'],row['Profit'],row['Min_water'],row['Min_past_rainfall'],row['Crop_duration']])

with open('./farmars.csv') as farmar:
	farmar_reader=csv.DictReader(farmar)
	for row in farmar_reader:
		farmar_list.append([row['Farmar_id'],row['Name'],row['Punchayat'],row['Hamlet'],row['Welth'],row['Type']])

with open('./ww_count.csv') as wells_data:	# working wells data 5 years span wise
	well_reader=csv.DictReader(wells_data)
	for row in well_reader:
		ww_data_list.append([row['year'],row['ww_count']])

for r in ww_data_list:
	c_data_years.append(int(r[0]))
	c_data_wells.append(int(r[1]))

print("collected years")
print(c_data_years)
print("collected wells count")
print(c_data_wells)
y_working_wells=[] 	#Year wise working wells count
w_open_well=[]
w_tube_well=[]
years = []				#years for collecting year wise working wells

ww=0	#working wells count
dw=0	# dry wells count
wtw=0	# working tube wells
wow=0	#working open wells


def new_borewell():
	"Retun decidion of digging of new borewell"

	return






# simulate year+season-wise

for year in range(START_YEAR,END_YEAR+1, 1):
	#year_rainfall=sum(m_rainfall[year])
	for season in range(1,NUM_SEASONS+1,1): # SEASONS: Kharif(July to Oct), Rabi(Nov to Feb), Summer(Mar to June)
		if season==1:
			START_MONTH=7
			END_MONTH=10
		elif season==2:
			START_MONTH=11
			END_MONTH=14	#13=1,14=2
		elif season==3:
			START_MONTH=3
			END_MONTH=6

		
		#print(START_MONTH)
		#print(END_MONTH)


		for mon in range(START_MONTH,END_MONTH+1,1):	#monthly wise simulation, month contains approximately 30 days 
			if mon==13:
				month=1		#Jan
			elif mon==14:
				month=2		#Feb
			else:
				month=mon

			monthly_wells_water=[]
			if month == 2:	# month= feb
				NUM_DAYS=28
			else:
				NUM_DAYS=30

			rainfall=int(m_rainfall[year - START_YEAR][month+2]) #reading month rainfall 
			arr=[]
			day_rainfall=[0]*NUM_DAYS #create a (size 30) list with all are zeros
			size=1
			if rainfall < min_rainfall: #Distribute monthly rainfall in days by using normal distribution
				arr.append(rainfall)
			else:
				size=int(rainfall/min_rainfall)
				if size > NUM_DAYS:
					size=MAX_RAINY_DAYS	#max rainfall days in a month
				arr=np.round(np.random.normal(rainfall/size,1,size))
			for x in range(len(arr)):	#assign rainfall to days in month
				for y in range(15):
					r=np.random.randint(NUM_DAYS)
					if day_rainfall[r] == 0:
						day_rainfall[r]=arr[x]
						break

			#print(year,month)
			#print(rainfall)
			
			m_temp = [] 	# 
			for day in range(1,NUM_DAYS+1,1):		# Day wise simulation
				rainfall= day_rainfall[day-1] # int(s_rainfall[year-START_YEAR][season+1])
				#print("day rainfall %d" %rainfall)
				water_depth = water_depth - (rainfall*MM_TO_FEET*PERCOLATION / POROSITY)	# Groundwater recharge
				#print(water_depth)
				if water_depth < 1:		# set minimum water depth is 3 feets
					water_depth=3
				#print ("year %d ,month %d, day %d, water depth %d " % (year,month,day,water_depth))
				# discharge due to utilization or withdraw from ground
				#print(wells_list)
				working_wells=[] # storing working wells count day wise
				dry_wells = []		#storing not working wells count day wise
				day_wells_water=[]	#storing day wise water depth of wells
				c_date=str(month)+"/"+str(day)+"/"+str(year) 	#convert to date format
				current_date=time.strptime(c_date, "%m/%d/%Y")
				day_wells_water.append(c_date)
				ww=0	#working wells count
				dw=0	# dry wells count
				wtw=0	# working tube wells
				wow=0	#working open wells



				for well in range(len(wells_list)):		#  Check wells status
					if wells_list[well][6]==0:	# check end date
						end_date= time.strptime(str('2/22/2050'), "%m/%d/%Y")
					else:
						end_date= time.strptime(str(wells_list[well][6]), "%m/%d/%Y") #reading end date of well
					#print(end_date)
					#print(current_date)
					if current_date < end_date: 	# check with end date for computing water utilization
						well_depth=int(wells_list[well][2]) # well depth
						hp=float(wells_list[well][7])
						well_type=int(wells_list[well][8])
						x=float(wells_list[well][3])        # well location lat and long
						y=float(wells_list[well][4])
						
						#print(int(wells_list[well][2]))
						dep=well_depth-water_depth
						if dep > MIN_DEPTH:
							ww=ww+1		#count as working well which contains minimum water is 3 feet
							#print("inside")
							#print(ww)
							working_wells.append([x,y]) #minimum depth of the water to say as working well: 6 feet
							if well_type == 1: # if type = open well
								y=20	#yield in leters
								wow=wow+1
							elif well_type==2:	#if type = bore well
								y=30
								wtw=wtw+1
							yield_current_well=(y*hp)/well_depth
							water_depth = water_depth +(yield_current_well / (VILLAGE_AREA*POROSITY))	# Groundwater Discharge

						else:
							dw=dw+1		#dry wells
							dry_wells.append([x,y])

						day_wells_water.append(int(dep))
					else:
						day_wells_water.append(-1)
				d_wells_water.append(day_wells_water) #append daily wells status
				m_temp.append(day_wells_water)
				#print(day_wells_water)	#
				working_well=np.asarray(working_wells)  #convert list to array
				dry_well=np.asarray(dry_wells)
				#water_depth = water_depth +(len(working_well)*YIELD_PER_WELL / (VILLAGE_AREA*POROSITY))
				#print(water_depth)
				#print(len(working_well))
				no_working_well.append(ww)
				no_dry_well.append(dw)
				tt=float(year+float(month/100.0)+float(day/100.0))
				#print(tt)
				time_period.append(tt)
			#print (m_temp)
			#print(len(m_temp[0]))
			#print(len(m_temp))
			monthly_wells_water.append(str(year)+"_"+str(month))
			for x in range(1,len(m_temp[0])):
				sum=0
				for y in range(0,len(m_temp),1):
					sum=sum+m_temp[y][x]
				monthly_wells_water.append(sum/len(m_temp))
			m_wells_water.append(monthly_wells_water)
			monthly_wells_water=[]



	if year >= TUBE_WELLS_TECH and water_depth < MAX_WATER_DEPTH:	# Dig bore well when water not reached to high depth
		if water_depth >= AVG_DEPTH:	# Check open wells are working or not(max open well depth is 70 feet)
			for n in range(int(TOTAL_WELLS*0.25)):	# If open wells are not working start digging more bore wells
				if year >= (TUBE_WELLS_TECH+10):
					well_depth=np.random.randint(400,900) #tube well depth between 400 to 900
        		else:
        			well_depth=np.random.randint(300,400)	#tube well depth between 300 to 400
        		wells_list.append(100,100,well_depth,79.0726490329,13.5493944246,current_date,12/30/2050,7,2,3)
        		#TUBE_WELLS.append(well_depth)
        else:										# other wise only 5% wells increased every year
        	for n in range(int(TOTAL_WELLS*0.20)):
        		if year >= (TUBE_WELLS_TECH+10):
        			well_depth=np.random.randint(400,800)
        		else:
        			well_depth=np.random.randint(300,400)
        		wells_list.append([100,100,well_depth,79.0726490329,13.5493944246,current_date,12/30/2050,7,2,3])
        		#TUBE_WELLS.append(well_depth)

	y_working_wells.append(ww)
	years.append(year)
	w_open_well.append(wow)
	w_tube_well.append(wtw)
#print(years)
#print(y_working_wells)
#print("no of working well")
#print(no_working_well)
z=0
wc=[]
yy=[]
for a in range(1960,2002):
	if a%5==0:
		wc.append(y_working_wells[z])
	z=z+1
wc.append(y_working_wells[z])
print("wc",wc)
w_wells=np.asarray(wc)

wells_data=np.asarray(ww_data_list)
no_working_wells=np.asarray(no_working_well)
no_dry_wells = np.asarray(no_dry_well)
time_periods=np.asarray(time_period)
year_working_wells=np.asarray(y_working_wells)
years_x=np.asarray(years)
w_open_wells=np.asarray(w_open_well)
w_tube_wells=np.asarray(w_tube_well)
#print("working open wells")
#print(w_open_wells)
#print("working tube wells")
#print(w_tube_wells)

"""x = w_wells
# create an index for each tick position
xi = [i for i in range(0, len(x))]
y = ww_data_wells
plt.ylim(0,400)
# plot the index for the x-values
plt.plot(xi, marker='o', linestyle='--', color='r', label='Square') 
plt.xlabel('x')
plt.ylabel('y') 
plt.xticks(xi, x)
plt.title('compare')
plt.legend() 
plt.show()"""


"""xnew = np.linspace(w_wells.min(),w_wells.max(),300) #300 represents number of points to make between T.min and T.max
power_smooth = spline(ww_data_years,w_wells,xnew)"""

"""xnew = np.linspace(year_working_wells.min(),year_working_wells.max(),30)
power_smooth = spline(years_x,year_working_wells,xnew)
plt.plot(xnew,power_smooth)"""


"""f=plt.figure("working open_wells")
plt.xlabel("Time in decades")
plt.ylabel("no_working wells")
plt.plot(years_x,w_open_wells)
f.show()"""

g=plt.figure("working_wells")
#plt.ylim(0,400)
plt.xlabel("Years")
plt.ylabel("no_working wells")
plt.plot(c_data_years,w_wells, label='Simulation')
plt.plot(c_data_years,c_data_wells, label='Collected' )
plt.legend()
g.show()
#plt.plot(years_x,year_working_wells)
#plt.plot(time_periods,no_working_wells)

#plt.axis(1900,2010,0,150)
plt.show()


#print(no_working_well)
#print(time_period)
#print(len(no_working_well))
#print(len(time_period))"""
"""#print(m_wells_water)
print(len(m_wells_water[0]))
print(len(m_wells_water))
print(m_wells_water[len(m_wells_water)-1][0])"""

"""workbook1 = xlsxwriter.Workbook('daily_wells_water.xls')
sheet1 = workbook1.add_worksheet('daily')

for x in range(0,len(d_wells_water[1])-1,1):
	for y in range(0,len(d_wells_water)-1,1):
		sheet1.write(x,y,d_wells_water[y][x])
workbook1.close()"""

"""workbook2 = xlsxwriter.Workbook('monthly_wells_water.xls')
sheet2 = workbook2.add_worksheet('monthly')

for x in range(0,len(m_wells_water[1])-1,1):
	for y in range(0,len(m_wells_water)-1,1):
		sheet2.write(x,y,m_wells_water[y][x])
workbook2.close()"""




			