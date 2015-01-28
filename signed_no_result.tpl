<html>
<head>
<title>DigAny, I digged followings for '{{search}}'</title>
</style>
</head>

<body>
<table width = "1200">
<tr>

<td width = "400" valign = "top">
<a href="/">
<img src="https://fbcdn-sphotos-g-a.akamaihd.net/hphotos-ak-xap1/v/t1.0-9/10459887_10154750525085408_476911929531417693_n.jpg?oh=ec152b1299e055a761c773df8b8f15df&oe=54D89A65&__gda__=1427564892_5657e50529a423e358e6564df5cf3d0e"></a>
</td>

<td align = "right" valign= "top">
<form action="/signedin" method="post"><input type="submit" name="check" value="Anonymous Mode"><input type="submit" name="check" value="Sign Out"></form>

<table>
<tr><td>
% if picture != None:
<img src={{picture}} alt={{name}} height='50' width='50'>
% end

<td>
<table><tr>
<tr><td>
% if name != None:
Name: {{name}}
% end
</td></tr>

<tr><td>
% if family_name != None:
Family name: {{family_name}}
% end
</td></tr>

<tr><td>
% if gender != None:
Gender: {{gender}}
% end
</td></tr>

<tr><td>
Email: {{email}}
</td></tr>

</tr>
</table>
</td>
</tr>
</table>

</td>
</tr>
</table>

<form action="/signedin" method="post"><input type="text" name="keywords" size='80'><input type="submit" name="check" value="Search"></form>

No result for '{{search}}'

</body>
</html>
