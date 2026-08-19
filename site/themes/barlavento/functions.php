<?php
/**
 * Barlavento child theme.
 *
 * Design lives in theme.json and in files under assets/ — never in the
 * database. That is what keeps the eventual move to the commons repo lossless.
 */

// Landing page: the [bl_home] shortcode that renders the three network streams.
require_once __DIR__ . '/inc/home-render.php';

// Landing stylesheet — only on the front page.
add_action( 'wp_enqueue_scripts', function () {
	if ( is_front_page() ) {
		wp_enqueue_style(
			'barlavento-home',
			get_stylesheet_directory_uri() . '/assets/home.css',
			array(),
			// filemtime, not a hand-kept string: the stylesheet then cache-busts
			// itself on every edit. A stale CSS after a change is invisible and
			// wastes a debugging cycle each time.
			(string) @filemtime( get_stylesheet_directory() . '/assets/home.css' )
		);
	}
} );

add_action( 'wp_enqueue_scripts', function () {
	wp_enqueue_style(
		'barlavento-maps',
		get_stylesheet_directory_uri() . '/assets/maps.css',
		array(),
		(string) @filemtime( get_stylesheet_directory() . '/assets/maps.css' )
	);
} );

/**
 * Layout experiments.
 *
 * Two alternate desktop layouts are being trialled against the centred
 * baseline. Rather than custom templates, a body class is derived from the page
 * slug — the same content can then be rendered three ways with nothing but CSS,
 * and any of them can be deleted without residue.
 */
add_filter( 'body_class', function ( $classes ) {
	if ( ! is_page() ) {
		return $classes;
	}
	$slug = get_post_field( 'post_name', get_queried_object_id() );
	// Sticky is the adopted layout for the two canonical demo pages; the
	// -sticky / -asym suffixed pages remain as side-by-side trials.
	$sticky_pages = array( 'ercb-community', 'ercb-projects', 'ercb-network-live' );
	if ( in_array( $slug, $sticky_pages, true ) || str_ends_with( $slug, '-sticky' ) ) {
		$classes[] = 'layout-sticky';
	} elseif ( str_ends_with( $slug, '-asym' ) ) {
		$classes[] = 'layout-asym';
	}
	// Per-map tuning: the Restor embed needs a wider column than the D3 social
	// map (below ~960px Restor drops into its stacked/mobile mode, which our
	// fixed-height frame slices badly). Tag the two page families so the sticky
	// grid can size each map's column independently.
	if ( str_contains( $slug, 'ercb-projects' ) ) {
		$classes[] = 'map-restor';
	} elseif ( str_contains( $slug, 'ercb-community' ) || str_contains( $slug, 'ercb-network-live' ) ) {
		// The live network page is a D3 graph like the social map, so it wants
		// the same column width — not Restor's wider one.
		$classes[] = 'map-social';
	}
	return $classes;
} );

add_action( 'wp_enqueue_scripts', function () {
	wp_enqueue_style(
		'barlavento-layouts',
		get_stylesheet_directory_uri() . '/assets/layouts.css',
		array( 'barlavento-maps' ),
		'0.2.2'
	);
} );

add_action( 'wp_enqueue_scripts', function () {
	wp_enqueue_script(
		'barlavento-map-fullscreen',
		get_stylesheet_directory_uri() . '/assets/map-fullscreen.js',
		array(),
		(string) @filemtime( get_stylesheet_directory() . '/assets/map-fullscreen.js' ),
		true
	);
} );
