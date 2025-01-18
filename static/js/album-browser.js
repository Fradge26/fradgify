$(document).ready(function () {
    // Function to fetch artist and album data
    function fetchAlbumData() {
        $.getJSON('/static/json/albums.json', function(data) {
            const tableData = [];

            // Loop through artists and albums
            data.albums.forEach(album => {
                tableData.push([
                    album.artist,
                    album.album,
                    album.year,
                    album.path,
                    `<button class="play-button" data-path="${album.path}" aria-label="Play Album">
                        <img src="/static/icons/play_circle_37dp_007BFF_FILL0_wght700_GRAD0_opsz40.svg" alt="Play" width="24" height="24">
                    </button>`
                ]);
        
            });

            // Populate the DataTable
            $('#albums').DataTable({
                data: tableData,
                order: [[0, "asc"], [2, "dsc"]],
                columns: [
                    { title: "Artist" },
                    { title: "Album" },
                    { title: "Year" },
                    { title: "Path", visible: false},
                    { title: "" }
                ]
            });
            
        }).fail(function() {
            console.error('Error fetching album data.');
        });
    }

    // Fetch the album data on document ready
    fetchAlbumData();

    // Handle play button click
    $(document).on('click', '.play-button', function() {
        const folderPath = $(this).data('path');
        console.log(folderPath)
        // Call your function to play the album here
        const encodedPath = encodeURIComponent(folderPath);
        console.log(encodedPath)
        window.location.href = `/music/play/?path=${encodedPath}`;
    });
});
