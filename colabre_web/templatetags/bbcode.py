import re
from django import template
register = template.Library()

@register.filter
def bbcode(value):

	bbdata = [
		(r'\[font=(.+?)\](.+?)\[/font\]', r'<span style="font-family: \1">\2</span>'),
		(r'\[color=(.+?)\](.+?)\[/color\]', r'<span style="color: \1">\2</span>'),
		(r'\[url\](.+?)\[/url\]', r'<a href="\1">\1</a>'),
		(r'\[url=(.+?)\](.+?)\[/url\]', r'<a href="\1">\2</a>'),
		(r'\[email\](.+?)\[/email\]', r'<a href="mailto:\1">\1</a>'),
		(r'\[email=(.+?)\](.+?)\[/email\]', r'<a href="mailto:\1">\2</a>'),
		(r'\[img\](.+?)\[/img\]', r'<img src="\1">'),
		(r'\[img=(.+?)\](.+?)\[/img\]', r'<img src="\1" alt="\2">'),
		(r'\[b\](.+?)\[/b\]', r'<b>\1</b>'),
		(r'\[i\](.+?)\[/i\]', r'<i>\1</i>'),
		(r'\[u\](.+?)\[/u\]', r'<u>\1</u>'),
		(r'\[quote\](.+?)\[/quote\]', r'<div style="margin-left: 1cm">\1</div>'),
		(r'\[center\](.+?)\[/center\]', r'<div style="text-align: center;">\1</div>'),
		(r'\[left\](.+?)\[/left\]', r'\1'),
		(r'\[right\](.+?)\[/right\]', r'<div style="text-align: right;">\1</div>'),
		(r'\[justify\](.+?)\[/justify\]', r'\1'),
		(r'\[code\](.+?)\[/code\]', r'<tt>\1</tt>'),
		(r'\[big\](.+?)\[/big\]', r'<big>\1</big>'),
		(r'\[small\](.+?)\[/small\]', r'<small>\1</small>'),
		
		# customs
		(r'\[size=7\](.+?)\[/size\]', r'<span style="font-size: 40px;">\1</span>'),
		(r'\[size=6\](.+?)\[/size\]', r'<span style="font-size: 32px;">\1</span>'),
		(r'\[size=5\](.+?)\[/size\]', r'<span style="font-size: 24px;">\1</span>'),
		(r'\[size=4\](.+?)\[/size\]', r'<span style="font-size: 18px;">\1</span>'),
		(r'\[size=3\](.+?)\[/size\]', r'<span style="font-size: 16px;">\1</span>'),
		(r'\[size=2\](.+?)\[/size\]', r'<span style="font-size: 13px;">\1</span>'),
		(r'\[size=1\](.+?)\[/size\]', r'<span style="font-size: 10px;">\1</span>'),
		]

	for bbset in bbdata:
		p = re.compile(bbset[0], re.DOTALL)
		value = p.sub(bbset[1], value)

	#The following two code parts handle the more complex list statements
	temp = ''
	p = re.compile(r'\[list\](.+?)\[/list\]', re.DOTALL)
	m = p.search(value)
	if m:
		items = re.split(re.escape('[*]'), m.group(1))
		for i in items[1:]:
			temp = temp + '<li>' + i + '</li>'
		value = p.sub(r'<ul>'+temp+'</ul>', value)

	temp = ''
	p = re.compile(r'\[list=(.)\](.+?)\[/list\]', re.DOTALL)
	m = p.search(value)
	if m:
		items = re.split(re.escape('[*]'), m.group(2))
		for i in items[1:]:
			temp = temp + '<li>' + i + '</li>'
		value = p.sub(r'<ol type=\1>'+temp+'</ol>', value)

	return value