---
layout: default
title: By Name
permalink: /name/
pagination: 
  enabled: true
  category: 1001
  permalink: /:num/
  sort_field: 'title'
  sort_reverse: false
---

<!-- _layouts/home.html -->
{% for post in paginator.posts %}
	<a href="{{ post.url | relative_url }}">
      <strong>{{ post.title | escape }}</strong>
	</a>
{% endfor %}
{% if paginator.total_pages > 1 %}
  <ul class="pager">
    {% if paginator.previous_page %}
    <li>
      <a class="previous" href="{{ paginator.previous_page_path | prepend: site.baseurl | replace: '//', '/' }}">&larr; 이전</a>
    </li>
    {% endif %}
    {% if paginator.next_page %}
    <li>
      <a class="next" href="{{ paginator.next_page_path | prepend: site.baseurl | replace: '//', '/' }}">다음 &rarr;</a>
    </li>
    {% endif %}
  </ul>
{% endif %}
