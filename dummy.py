n=1000000
a=0
ans=0
st=0
while n>0:
    
    a=n
    count=0
    while(a>1):
        count+=1
        if a%2==0:
            a=a/2
        else:
            a=3*a+1
    if(count>ans):
        ans=count
        st=n

    n=n-1
print(ans,st)
        

