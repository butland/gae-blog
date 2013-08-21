$(function () {
    $.fn.imagesLoaded = function (callback) {
        var $images = this.find('img'),
            len = $images.length,
            _this = this,
            blank = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==';

        function triggerCallback() {
            callback.call(_this, $images);
        }

        function imgLoaded() {
            if (--len <= 0 && this.src !== blank) {
                setTimeout(triggerCallback);
                $images.off('load error', imgLoaded);
            }
        }

        if (!len) {
            triggerCallback();
        }

        $images.on('load error', imgLoaded).each(function () {
            // cached images don't fire load sometimes, so we reset src.
            if (this.complete || this.complete === undefined) {
                var src = this.src;
                // webkit hack from http://groups.google.com/group/jquery-dev/browse_thread/thread/eee6ab7b2da50e1f
                // data uri bypasses webkit log warning (thx doug jones)
                this.src = blank;
                this.src = src;
            }
        });

        return this;
    };

    // gallery container
    var $rgGallery = $('#rg-gallery');
    // carousel container
    var $esCarousel = $rgGallery.find('div.es-carousel-wrapper');
    // the carousel items
    var $items = $esCarousel.find('ul > li');
    // total number of items
    var itemsCount = $items.length;

    var Gallery = (function () {
        // index of the current item
        var current = 0;
        // mode : carousel || fullview
        var mode = 'carousel';
        // control if one image is being loaded
        var anim = false;
        var init = function () {
            $items.add('<img src="/images/ajax-loader.gif"/>').imagesLoaded(function () {
                // add options
                _addViewModes();
                // add large image wrapper
                _addImageWrapper();
                // show first image
                _showImage($items.eq(current));

                // pre load second image
                if (current + 1 < itemsCount)
                    _preLoadImg($items.eq(current + 1));
            });

            // initialize the carousel
            if (mode === 'carousel')
                _initCarousel();
        };

        var _initCarousel = function () {
            // we are using the elastislide plugin:
            // http://tympanus.net/codrops/2011/09/12/elastislide-responsive-carousel/
            $esCarousel.show().elastislide({
                imageW: 72,
                border: 0,
                onClick: function ($item) {
                    if (anim) return false;
                    anim = true;
                    // on click show image
                    _showImage($item);
                    // change current
                    current = $item.index();

                    var next = (current + 1) % itemsCount;
                    _preLoadImg($items.eq(next));
                    return false;
                }
            });

            // set elastislide's current to current
            $esCarousel.elastislide('setCurrent', current);

        };

        var _addViewModes = function () {
            var $viewfull = $('#rg-view-full');
            var $viewthumbs = $('#rg-view-thumbs');

            $viewfull.on('click.rgGallery', function (event) {
                if (mode === 'carousel')
                    $esCarousel.elastislide('destroy');
                $esCarousel.hide();
                $viewfull.addClass('rg-view-selected');
                $viewthumbs.removeClass('rg-view-selected');
                mode = 'fullview';
                return false;
            });

            $viewthumbs.on('click.rgGallery', function (event) {
                _initCarousel();
                $viewthumbs.addClass('rg-view-selected');
                $viewfull.removeClass('rg-view-selected');
                mode = 'carousel';
                return false;
            });

            if (mode === 'fullview')
                $viewfull.trigger('click');

        };
        var _addImageWrapper = function () {
            if (itemsCount > 1) {
                // addNavigation
                var $navPrev = $rgGallery.find('a.rg-image-nav-prev'),
                    $navNext = $rgGallery.find('a.rg-image-nav-next'),
                    $imgWrapper = $rgGallery.find('div.rg-image');

                $navPrev.on('click.rgGallery', function (event) {
                    _navigate('left');
                    return false;
                });

                $navNext.on('click.rgGallery', function (event) {
                    _navigate('right');
                    return false;
                });

                $(document).on('keyup.rgGallery', function (event) {
                    if (event.keyCode == 39)
                        _navigate('right');
                    else if (event.keyCode == 37)
                        _navigate('left');
                });

            }

        };

            // navigate through the large images
        var _navigate = function (dir) {
            if (anim) return false;
            anim = true;
            var next;
            if (dir === 'right') {
                current = (current + 1) % itemsCount;
                next = (current + 1) % itemsCount;
            } else if (dir === 'left') {
                --current;
                if (current < 0)
                    current += itemsCount;
                next = current - 1;
                if (next < 0)
                    next += itemsCount;
            }

            _preLoadImg($items.eq(next));
            _showImage($items.eq(current));
            return false;
        };

            // show current big image, called by  _navigate
        var _showImage = function ($item) {

            var $loader = $rgGallery.find('div.rg-loading').show();

            $items.removeClass('selected');
            $item.addClass('selected');

            var $thumb = $item.find('img'),
                largesrc = $thumb.data('large'),
                title = $thumb.data('description');

            $('<img/>').load(function () {
                $rgGallery.find('div.rg-image').empty().append('<img src="' + largesrc + '"/>');
                if (title) {
                    $rgGallery.find('div.rg-caption').show().text(title);
                } else {
                    $rgGallery.find('div.rg-caption').hide();
                }
                $loader.hide();

                if (mode === 'carousel') {
                    $esCarousel.elastislide('reload');
                    $esCarousel.elastislide('setCurrent', current);
                }

                anim = false;

            }).attr('src', largesrc);

        };

        var _preLoadImg = function ($item) {
            new Image().src = $item.find('img').data('large');
        };

        var addItems = function ($new) {
            $esCarousel.find('ul').append($new);
            $items = $items.add($($new));
            itemsCount = $items.length;
            $esCarousel.elastislide('add', $new);
        };

        return {
            init: init,
            addItems: addItems
        };

    })();

    Gallery.init();
});