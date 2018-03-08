window.onload = function() {
  let objects, transitions, currentpage = -1;
  const floater = document.getElementById('floater'),
    header = document.getElementById('header'),
    searchbar = document.getElementById('searchbar'),
    showunreleased = document.getElementById('showunreleased'),
    searchobjects = document.getElementById('searchobjects'),
    viewpage = document.getElementById('viewpage');

  function tooltip(text) {
    floater.innerHTML = text;
    floater.style.display = 'block';
  }

  function hideTooltip() {
    floater.style.display = 'none';
  }

  document.addEventListener('mousemove', (e) => {
    floater.style.left = e.clientX + 5;
    floater.style.top = e.clientY + 5;
  });

  function showPage(id) {
    header.classList.add('retracted');
    document.querySelectorAll('.page').forEach(page => {
      if (page.id == id) {
        page.style.display = '';
      } else {
        page.style.display = 'none';
      }
    });
  }

  function navigate(oid) {
    if (currentpage == oid)
      return;

    let page = window.location.pathname;

    if (oid === null) {
      showPage('searchpage');
    } else {
      page = '#' + oid.toString();
      renderViewPage(objects[oid]);
      showPage('viewpage');
    }

    history.pushState(oid, document.title, page);
    currentpage = oid;
  }

  window.onpopstate = (e) => {
    console.log(e);
  };

  function renderThumbnail(obj, size, clickable) {
    let thumb = document.createElement('div')
    thumb.dataset.oid = obj.id;
    thumb.dataset.name = obj.name;
    thumb.dataset.released = (obj.version !== null);
    thumb.classList.add('thumbnail');
    thumb.style.cssText = `background-image: url("${obj.sprite}"), url("grass.png");`;
    thumb.style.width = size;

    if (clickable) {
      thumb.classList.add('clickable');
      thumb.addEventListener('mouseover', () => tooltip(obj.name));
      thumb.addEventListener('mouseout', hideTooltip);
      thumb.addEventListener('click', () => navigate(obj.id));
    }

    return thumb;
  }

  function renderViewPage(obj) {
    viewpage.querySelector('#viewthumb').innerHTML = "";
    viewpage.querySelector('#viewthumb').appendChild(renderThumbnail(obj, 128, false));
    viewpage.querySelector('#viewoid').innerHTML = obj.id;
    viewpage.querySelector('#viewname').innerHTML = obj.name;
  }

  function refilterObjects() {
    const search = searchbar.value.toLowerCase(),
      includeUnreleased = showunreleased.checked;

    document.querySelectorAll('#searchobjects > .thumbnail').forEach(thumb => {
      if (thumb.dataset.name.toLowerCase().includes(search) &&
        (includeUnreleased || thumb.dataset.released === 'true')) {
        thumb.style.display = '';
      } else {
        thumb.style.display = 'none';
      }
    });
  }

  searchbar.addEventListener('input', () => {
    header.classList.add('retracted');

    refilterObjects()
    navigate(null);
  });

  searchbar.addEventListener('focus', () => {
    if (searchbar.value) navigate(null);
  });

  showunreleased.addEventListener('change', () => refilterObjects());

  // Load objects and transitions, and render the searh page.
  fetch('ohol.json')
    .then(response => response.json())
    .then(json => {
      objects = json.objects;
      transitions = json.transitions;

      // We got linked directly to an object.
      if (window.location.hash) {
        const oid = parseInt(window.location.hash.substring(1));
        if (oid !== NaN && objects[oid]) {
          currentpage = oid;
          renderViewPage(objects[oid])
          showPage('viewpage');
        }
      }

      Object.values(objects).forEach((obj) => {
        searchobjects.appendChild(renderThumbnail(obj, 128, true));
      });

      document.getElementById('loading').remove();
    });
}