/**
 * Full-screen control for embedded maps.
 *
 * The button goes on the wrapper, not the iframe: calling requestFullscreen()
 * on the container takes the iframe with it, which avoids needing cooperation
 * from the embedded document (we do not control Restor's page).
 */
( function () {
	'use strict';

	function label( isFull ) {
		return isFull ? '⤢  Exit full screen' : '⤢  View full screen';
	}

	function addControl( frame ) {
		var button = document.createElement( 'button' );
		button.type = 'button';
		button.className = 'ercb-fullscreen-btn';
		button.textContent = label( false );
		button.setAttribute( 'aria-label', label( false ) );

		button.addEventListener( 'click', function () {
			if ( document.fullscreenElement === frame ) {
				document.exitFullscreen();
			} else if ( frame.requestFullscreen ) {
				/* Read activation NOW, synchronously. It is *transient* and has
				   already lapsed by the time the promise rejects, so reading it
				   inside the catch reports a misleading "false" on a click that
				   really did carry a gesture — which sends the next person
				   debugging this straight down the wrong path. */
				var hadActivation = navigator.userActivation
					? navigator.userActivation.isActive
					: 'unknown';
				frame.requestFullscreen().catch( function ( err ) {
					/* Denied or unsupported — leave the inline view as-is, but
					   say so. A bare catch here made this fail silently: the
					   button looked dead, with no way to tell a real denial
					   from a broken control without instrumenting it by hand. */
					console.warn(
						'[ercb] Full screen refused:',
						err && err.name, err && err.message,
						'· userActivation at click:', hadActivation
					);
				} );
			} else if ( frame.webkitRequestFullscreen ) {
				frame.webkitRequestFullscreen();
			} else {
				/* iPhone Safari implements no element full-screen API at all —
				   only <video> can go full screen. Both branches above are
				   absent, so the button was silently dead on phones, which is
				   exactly where the inline map is least usable. Opening the
				   map's own URL in a new tab is the closest equivalent: it
				   gets the whole viewport and the browser's own back button. */
				var inner = frame.querySelector( 'iframe' );
				if ( inner && inner.src ) {
					window.open( inner.src, '_blank', 'noopener' );
				}
			}
		} );

		/* Say what the button will actually do on this device. */
		if ( ! frame.requestFullscreen && ! frame.webkitRequestFullscreen ) {
			button.textContent = '⤢  Open full map';
			button.setAttribute( 'aria-label', 'Open the full map in a new tab' );
		}

		frame.appendChild( button );
	}

	function sync() {
		document.querySelectorAll( '.ercb-fullscreen-btn' ).forEach( function ( b ) {
			var isFull = document.fullscreenElement === b.parentNode;
			b.textContent = label( isFull );
			b.setAttribute( 'aria-label', label( isFull ) );
		} );
	}

	document.addEventListener( 'DOMContentLoaded', function () {
		document.querySelectorAll( '.ercb-frame' ).forEach( addControl );
	} );
	document.addEventListener( 'fullscreenchange', sync );
	document.addEventListener( 'webkitfullscreenchange', sync );
}() );
