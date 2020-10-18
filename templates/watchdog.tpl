{% args d %}
<html><head> <title> {{d["name"]}} </title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,">
<link href="style.css" rel="stylesheet">
</head>
<body> <h1>{{d["name"]}}</h1>

<p>Started at {{d["ntp"]}}</p>

<p>Watchdog 1 reset at {{d["wd1"]}}</p>

<p><a href="/on_1"><button class="button">Turn ON 1</button></a></p>
<p><a href="/off_1"><button class="button button2">Turn OFF 1</button></a></p>
<p><a href="/restart_1"><button class="button button3">Restart 1</button></a></p>

<p>Watchdog 2 reset at {{d["wd2"]}}</p>

<p><a href="/on_2"><button class="button">Turn ON 2</button></a></p>
<p><a href="/off_2"><button class="button button2">Turn OFF 2</button></a></p>
<p><a href="/restart_2"><button class="button button3">Restart 2</button></a></p>
<p></p>
<p><a href="/">Reload</a></p>
</body></html>
