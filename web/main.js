window.onload = function() {
  let objects, transitions;
  const floater = document.getElementById('floater'),
    header = document.getElementById('header');

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

  let currentPage = -1;

  function showPage(oid) {
    if (currentPage == oid)
      return;

    let id = 'searchpage';
    if (oid !== null) {
      id = 'viewpage'
      renderViewPage(objects[oid]);
    }

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
    let page = window.location.pathname;
    if (oid !== null) {
      page = '#' + oid.toString();
    }

    showPage(oid);
    history.pushState(oid, document.title, page);
  }

  window.onpopstate = (e) => {
    showPage(e.state);
  };

  function renderThumbnail(obj, size, clickable) {
    let thumb = document.createElement('div')
    thumb.dataset.oid = obj.id;
    thumb.classList.add('thumbnail');
    thumb.style.cssText = `background-image: url("${obj.sprite}"), url("grass.png");`;
    thumb.style.width = size;
    thumb.style.height = size;

    if (clickable) {
      thumb.classList.add('clickable');
      thumb.addEventListener('mouseover', () => tooltip(obj.name));
      thumb.addEventListener('mouseout', hideTooltip);
      thumb.addEventListener('click', () => navigate(obj.id));
    }

    return thumb;
  }

  const viewpage = document.getElementById('viewpage'),
    interactionsheader = document.getElementById('interactionsheader'),
    transitionshead = document.getElementById('transitionshead'),
    viewthumb = document.getElementById('viewthumb'),
    viewoid = document.getElementById('viewoid'),
    viewname = document.getElementById('viewname'),
    viewproperties = document.getElementById('viewproperties'),
    viewactortransitions = document.getElementById('viewactortransitions'),
    viewtargettransitions = document.getElementById('viewtargettransitions'),
    viewtimedtransitions = document.getElementById('viewtimedtransitions');

  function renderTransition(t) {
    let formula = document.createElement('div');
    formula.classList.add('transition');
    formula.innerHTML = `
      <span class="actor"></span>
      <span class="plus">+</span>
      <span class="target"></span>
      =
      <span class="newactor"></span>
      <span class="newtarget"></span>
    `;

    let actor = formula.querySelector('.actor'),
      target = formula.querySelector('.target'),
      newActor = formula.querySelector('.newactor'),
      newTarget = formula.querySelector('.newTarget');

    // If target is -1, we're putting something down (like an object in tongs).
    if (t.target > 0) {
      target.appendChild(
        renderThumbnail(objects[t.target], 64, true));
    }

    if (t.newTarget > 0) {
      newTarget.appendChild(
        renderThumbnail(objects[t.newTarget], 64, true));
    }

    if (t.timed) {
      if (t.time === -1)
        actor.innerHTML = 'epoch';
      else
        actor.innerHTML = t.time + 's';
    } else {
      if (t.actor < 1) {
        let hand = document.createElement('div');
        hand.classList.add('handthumbnail');
        actor.appendChild(hand);
      } else {
        actor.appendChild(
          renderThumbnail(objects[t.actor], 64, true));
      }

      // This happens when the actor joins the target. For example, sheep eating
      // carrots.
      if (t.newActor > 0) {
        newActor.appendChild(
          renderThumbnail(objects[t.newActor], 64, true));
      }
    }

    return formula;
  }

  function renderViewPage(obj) {
    viewthumb.innerHTML = "";
    viewthumb.appendChild(renderThumbnail(obj, 128, false));
    viewoid.innerHTML = obj.id;
    viewname.innerHTML = obj.name;

    viewactortransitions.innerHTML = "";
    viewtargettransitions.innerHTML = "";
    viewtimedtransitions.innerHTML = "";

    if (obj.actorTransitions.length > 0 || obj.targetTransitions.length > 0) {
      interactionsheader.style.display = '';
      obj.actorTransitions.forEach((t) =>
        viewactortransitions.appendChild(renderTransition(t)));
      obj.targetTransitions.forEach((t) =>
        viewtargettransitions.appendChild(renderTransition(t)));
    } else {
      interactionsheader.style.display = 'none';
    }

    if (obj.timedTransitions.length > 0) {
      transitionsheader.style.display = '';
      obj.timedTransitions.forEach((t) =>
        viewtimedtransitions.appendChild(renderTransition(t)));
    } else {
      transitionsheader.style.display = 'none';
    }
  }

  const searchobjects = document.getElementById('searchobjects'),
    searchbar = document.getElementById('searchbar'),
    showcategories = document.getElementById('showcategories'),
    showunreleased = document.getElementById('showunreleased');

  let filterTimer;

  function refilterObjects() {
    const search = searchbar.value.toLowerCase(),
      includeUnreleased = showunreleased.checked,
      includeCategories = showcategories.checked;

    document.querySelectorAll('#searchobjects > .thumbnail').forEach(thumb => {
      const obj = objects[parseInt(thumb.dataset.oid)];
      if ((thumb.dataset.oid == search ||
          obj.name.toLowerCase().includes(search)) &&
        (includeUnreleased || obj.version !== null) &&
        (includeCategories || obj.category !== true)) {
        thumb.style.display = '';
      } else {
        thumb.style.display = 'none';
      }
    });
  }

  searchbar.addEventListener('input', () => {
    header.classList.add('retracted');

    clearTimeout(filterTimer);
    filterTimer = setTimeout(refilterObjects, 100);
    navigate(null);
  });

  searchbar.addEventListener('focus', () => {
    if (searchbar.value) navigate(null);
  });

  showunreleased.addEventListener('change', () => refilterObjects());
  showcategories.addEventListener('change', () => refilterObjects());

  // Load objects and transitions, and render the searh page.
  fetch('ohol.json')
    .then(response => response.json())
    .then(json => {
      objects = json.objects;
      interactions = new Map();
      transitions = new Map();

      // Map interactions to objects.
      Object.values(objects).forEach((obj) => {
        obj.actorTransitions = new Array();
        obj.targetTransitions = new Array();
        obj.timedTransitions = new Array();
      })

      Object.values(json.transitions).forEach(t => {
        if (t.timed) {
          if (t.target > 0) objects[t.target].timedTransitions.push(t);
          if (t.newTarget > 0) objects[t.newTarget].timedTransitions.push(t);
        } else {
          if (t.actor > 0) objects[t.actor].actorTransitions.push(t);
          if (t.target > 0) objects[t.target].targetTransitions.push(t);
          if (t.newActor > 0) objects[t.newActor].actorTransitions.push(t);
          if (t.newTarget > 0) objects[t.newTarget].targetTransitions.push(t);
        }
      });

      // If an object has a 'last use' transition, delete its counterpart.
      Object.values(objects).forEach((obj) => {
        lastTargetTransition = obj.targetTransitions.find((t) => t.lastTarget)
        if (lastTargetTransition !== undefined) {
          obj.targetTransitions.splice(obj.targetTransitions.findIndex((t) =>
            t.target === lastTargetTransition.target &&
            t.actor === lastTargetTransition.actor &&
            !t.lastTarget
          ), 1);
        }

        lastActorTransition = obj.targetTransitions.find((t) => t.lastActor)
        if (lastActorTransition !== undefined) {
          obj.targetTransitions.splice(obj.targetTransitions.findIndex((t) =>
            t.target === lastActorTransition.target &&
            t.actor === lastActorTransition.actor &&
            !t.lastActor
          ), 1);
        }

        // // Put target before newTarget and actor before newActor.
        // obj.actorTransitions.sort((a, b) =>
        //   (a.actor === obj.actor ? 1 : 0) - (b.actor === obj.actor ? 1 : 0)
        // );
        //
        // obj.targetTransitions.sort((a, b) =>
        //   (a.target === obj.target ? 1 : 0) - (b.target === obj.target ? 1 : 0)
        // );
        //
        // obj.timedTransitions.sort((a, b) =>
        //   (a.target !== obj.target ? 1 : 0) - (b.target !== obj.target ? 1 : 0)
        // );
      })

      // We got linked directly to an object.
      if (window.location.hash) {
        const oid = parseInt(window.location.hash.substring(1));
        if (oid !== NaN && objects[oid]) {
          showPage(oid);
        }
      }

      // Finally, render the thumbnails.
      Object.values(objects).forEach((obj) => {
        searchobjects.appendChild(renderThumbnail(obj, 128, true));
      });

      document.getElementById('loading').remove();
    });
}