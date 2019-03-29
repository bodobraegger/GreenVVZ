var url = 'https://greenvvz.ifi.uzh.ch/'
var secret="secret"

fetch(url)
	.then(console.log)

fetch(url+'searchterms')
	.then(res=>res.json())
    .then(console.log)

fetch(url+'searchterms'+'?key='+secret, {
    method: 'POST',
    body: JSON.stringify({
      term: 'Sustainability',
    }),
    headers: {
     'Content-type': 'application/json; charset=UTF-8'
    }
})
    .then(console.log)

id=1
fetch(url+'searchterms/'+id+'?key='+secret, {
    method: 'DELETE',
    //body: JSON.stringify({
    //  title: 'foo',
    //  body: 'bar',
    //  userId: 1
    //}),
    headers: {
     'Content-type': 'application/json; charset=UTF-8'
    }
})
    .then(console.log)