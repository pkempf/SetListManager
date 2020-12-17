const BASE_URL = window.location.pathname.split("/")[0];
const SETLIST_ID = window.location.pathname.split("/")[2];

let setlistSongs = [];
let otherSongs = [];

// Functions for making HTML ----------------------------

function makeSetlistSongHTML(song) {
  return `
        <li id="song-li-${song.id}" data-id="${song.id}" class="alert alert-primary item" style="user-select: none;">||&nbsp
            <a href="/songs/${song.id}" target="_blank">${song.title}</a> <small>by ${song.artist}</small>
            <span class="badge badge-light float-right mt-1" style="cursor: pointer;" id="remove-song-${song.id}" data-id="${song.id}">X</span>
        </li>
    `;
}

function makeOtherSongHTML(song) {
  return `
        <li id="song-li-${song.id}" data-id="${song.id}" class="alert alert-primary item">
            <span class="badge badge-light" style="cursor: pointer;" data-id="${song.id}" id="add-song-${song.id}">&lt</span> 
            <a href="/songs/${song.id}" target="_blank">${song.title}</a> <small>by ${song.artist}</small>
        </li>
    `;
}

// Helper function for sorting
function compareSongs(a, b) {
  let a_title = a.title.toLowerCase();
  let b_title = b.title.toLowerCase();

  return a_title < b_title ? -1 : a_title > b_title ? 1 : 0;
}

// Helper function for verifying update
function arrayEquals(a, b) {
  if (!Array.isArray(a) || !Array.isArray(b) || a.length !== b.length) {
    return false;
  }
  for (i = 0; i < a.length; i++) {
    if (a[i] !== b[i]) {
      return false;
    }
  }
  return true;
}

// Displaying, filtering, moving songs ------------------

async function showSongsInitial() {
  let setlistSongsResponse = await axios.get(
    `${BASE_URL}/api/setlists/${SETLIST_ID}/get-songs`
  );

  setlistSongs = setlistSongsResponse.data.setlistSongs;
  otherSongs = setlistSongsResponse.data.otherSongs;

  for (let song of setlistSongs) {
    let newSong = $(makeSetlistSongHTML(song));
    $("#songs-in-setlist").append(newSong);
  }

  for (let song of otherSongs) {
    let newSong = $(makeOtherSongHTML(song));
    $("#songs-not-in-setlist").append(newSong);
  }

  sortable(".sortable");
}

function filterSongs() {
  if ($("#filter").is(":checked")) {
    let filterString = $("#filter-string").val().toLowerCase();
    for (let song of otherSongs) {
      if (filterString === "") {
        clearFilter();
      } else if (
        !(
          song.title.toLowerCase().includes(filterString) ||
          song.artist.toLowerCase().includes(filterString)
        )
      ) {
        $(`#song-li-${song.id}`).addClass("d-none");
      } else {
        $(`#song-li-${song.id}`).removeClass("d-none");
      }
    }
  } else {
    clearFilter();
  }
}

function clearFilter() {
  for (let song of otherSongs) {
    $(`#song-li-${song.id}`).removeClass("d-none");
  }
}

function addSongToSetlist(song) {
  let newHTML = makeSetlistSongHTML(song);
  let oldSongLocation = otherSongs.indexOf(song);

  setlistSongs.push(song);
  otherSongs.splice(oldSongLocation, 1);

  $(`#song-li-${song.id}`).remove();
  $("#songs-in-setlist").append($(newHTML));
}

function removeSongFromSetlist(song) {
  let newHTML = makeOtherSongHTML(song);
  let oldSongLocation = setlistSongs.indexOf(song);

  otherSongs.push(song);
  setlistSongs.splice(oldSongLocation, 1);

  $(`#song-li-${song.id}`).remove();

  otherSongs.sort(compareSongs);
  $("#songs-not-in-setlist").empty();

  for (let song of otherSongs) {
    let newSong = $(makeOtherSongHTML(song));
    $("#songs-not-in-setlist").append(newSong);
  }

  filterSongs();
}

// Event listeners --------------------------------------

$("#filter-string").on("input", function () {
  filterSongs();
});

$("#filter").on("click", function () {
  filterSongs();
});

$("#songs-in-setlist").on("click", "span", function () {
  let songIndex = setlistSongs
    .map(function (e) {
      return e.id;
    })
    .indexOf(parseInt($(this).data("id")));

  removeSongFromSetlist(setlistSongs[songIndex]);
  sortable(".sortable");
});

$("#songs-not-in-setlist").on("click", "span", function () {
  let songIndex = otherSongs
    .map(function (e) {
      return e.id;
    })
    .indexOf(parseInt($(this).data("id")));

  addSongToSetlist(otherSongs[songIndex]);
  sortable(".sortable");
});

$("#save-changes").on("click", async function () {
  let serializedSetlist = sortable(".sortable", "serialize");
  let updatedSetlistIDs = serializedSetlist[0].items.map(
    (x) => $(x.node).data().id
  );

  res = await axios.post(
    `${BASE_URL}/api/setlists/${SETLIST_ID}/update-songs`,
    {
      songs: updatedSetlistIDs,
      notes: $("#setlist-notes").val(),
    }
  );

  returnedIDs = res.data.songs.map((x) => x.id);
  if (arrayEquals(updatedSetlistIDs, returnedIDs)) {
    $("#success").show().delay(3000).fadeOut("slow");
  } else {
    alert("Something went wrong and the setlist was not successfully updated.");
  }
});

$(document).ready(function () {
  $("#success").hide();
  showSongsInitial();
});
