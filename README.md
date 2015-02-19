Statistical Arbitrage Mining for Display Advertising
===========

This is a repository of the experiment code supporting the paper "Statistical Arbitrage Mining for Display Advertising" submitted to KDD 2015.

For any problems, please report the issues here or contact [Weinan Zhang](http://www0.cs.ucl.ac.uk/staff/w.zhang/).

After pulling the repository, you could start from checking the single campaign arbitrage demo under the folder of scripts by running:
```
$ bash single_campaign_arbitrage_demo.sh 
```
After running, you could get the performance table printed in the console like:
```
prop	alpha	algo	profit	cvns	bids	imps	budget	cost	rratio	para	up
16	0.00100	const	-2.96	0	80000	740	339072	2958	0.2	5	0.0000
16	0.00100	rand	0.00	0	80000	0	339072	0	0.2	5	0.0000
16	0.00100	truth	44.72	3	80000	601	339072	11862	0.2	1	0.0000
16	0.00100	lin	-93.89	13	59404	10843	339072	339097	0.2	75	0.0000
16	0.00100	ortb	-131.61	11	55468	12556	339072	339091	0.2	290	0.0000
16	0.00100	sam1	45.77	6	80000	3148	339072	67405	0.2	25	0.0000
16	0.00100	sam1c	59.14	6	80000	1303	339072	54032	0.2	25	8.2433
16	0.00100	sam2	63.92	7	80000	4146	339072	68116	0.2	7.1	0.0000
16	0.00100	sam2c	60.63	7	80000	4146	339072	71408	0.2	7.1	0.7942
```

For the demo of multiple campaign arbitrage with portfolio selection, please run:
```
$ bash multiple_campaign_arbitrage_demo.sh 
```
and you can get the performance table printed in the console like:
```
prop	alpha	algo	profit	cvns	bids	imps	budget	cost	rratio	para	up
16	0.00100	const	54.33	2	80000	10527	410481	77991	0.2	17	0.0000
16	0.00100	rand	-105.69	0	80000	10309	410481	105690	0.2	29	0.0000
16	0.00100	truth	44.72	3	80000	601	410481	11862	0.2	1	0.0000
16	0.00100	lin	-184.14	12	40581	10983	410481	410491	0.2	105	0.0000
16	0.00100	ortb	-184.16	12	60043	14348	410481	410511	0.2	290	0.0000
16	0.00100	sam1	45.77	6	80000	3148	410481	67405	0.2	25	0.0000
16	0.00100	sam1c	49.06	6	80000	2202	410481	64108	0.2	25	3.9500
16	0.00100	sam2	66.64	7	80000	3905	410481	65391	0.2	6.5	0.0000
16	0.00100	sam2c	50.21	6	80000	3100	410481	62967	0.2	6.5	2.6962
16	0.10000	const	54.33	2	80000	10527	410481	77991	0.2	17	0.0000
16	0.10000	rand	-39.24	1	80000	10271	410481	105394	0.2	29	0.0000
16	0.10000	truth	44.72	3	80000	601	410481	11862	0.2	1	0.0000
16	0.10000	lin	-184.14	12	40581	10983	410481	410491	0.2	105	0.0000
16	0.10000	ortb	-184.16	12	60043	14348	410481	410511	0.2	290	0.0000
16	0.10000	sam1	45.77	6	80000	3148	410481	67405	0.2	25	0.0000
16	0.10000	sam1c	49.06	6	80000	2202	410481	64108	0.2	25	3.9500
16	0.10000	sam2	66.64	7	80000	3905	410481	65391	0.2	6.5	0.0000
16	0.10000	sam2c	50.21	6	80000	3100	410481	62967	0.2	6.5	2.6962
```
Note these results are produced from the very small data (the first 300,000 lines for each campaign in iPinYou). For the large-scale experiment, please first check our GitHub project [make-ipinyou-data](https://github.com/wnzhang/make-ipinyou-data) for pre-processing the iPinYou data. After downloading the dataset, by simplying `make all` you can generate the standardised data which will be used in the bid optimisation tasks.
