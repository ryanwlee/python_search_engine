<html>
<head>
<title>DigAny, I digged followings for '{{search}}'</title>
</style>
</head>

<body>
<a href="/">
<img src="https://scontent-a-lga.xx.fbcdn.net/hphotos-xpa1/v/t1.0-9/10393738_10154750525080408_7417565229542874316_n.jpg?oh=bc0a823cec3a5d642e65a6dac8ccf217&oe=5514E39A"></a>
<form action="/anonymous" method="post"><input type="text" name="keywords" size='80'><input type="submit" name="check" value="Search"><input type="submit" name="check" value="Sign In"></form><br>

<!-- Make table for results. Show word and its count -->
% page = int(page)
% i = (page/10+1)*10
% totalpage = len(result)

Total {{totalpage}} results<br>
Show from {{page+1}} to {{min(i,totalpage)}} results for '{{search}}'
% for k in range(page,min(i,len(result))):
<p><a href = {{result[k][0]}}>{{preview[k%10]}}</a>  {{result[k][0]}}</p>
 % page+=1
% end

<table width='600'><tr><td align='center'>
<table><tr>

% to = totalpage/10+1 if ((totalpage%10)!=0) else totalpage/10
% for pg in range(max(0,page/10-9),min(page/10+9,to)):
 % if pg == ((page-1)/10):
 <td>{{pg+1}} </td>
 % else:
  % newurl='http://localhost:8080/anonymous/'+search+'='+str(pg*10)
  <td><a href ={{newurl}}>{{pg+1}}</a> </td>
 % end
% end
</tr></table>

</td></tr></table>

</body>
</html>
