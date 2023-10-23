# Hybrid Search with Atlas Search & Vector Search

![Screenshot 2023-10-18 at 10 47 48](https://github.com/JuicySantos06/hybrid-search-atlas-search-vectorsearch/assets/84564830/9c4cbd11-d3bd-4a95-b03b-15f20f422231)

## General Information
> The following demo aims to demonstrate the ability to enhance the search experience through the joint use of both keyword-based and vector-based search technology.
> We will be using using the following native MongoDB technologies:
* MongoDB Atlas Search
* MongoDB Atlas Vector Search




### Step 1 : Import Cross-Market Recommendations dataset into your Atlas Database
> Download the US Home and Kitchen category dataset
```
link: https://xmrec.github.io/data/us/
```


### Step 2: Edit the 
```
Name = log_gen_server
AMI = Amazon Linux 2 AMI (HVM) - kernel 5.10, SSD Volume Type
Architecture = 64-bit (x86)
Instance type = c5.4xlarge
Inbound security rule = SSH (TCP, 22) from your IP
```