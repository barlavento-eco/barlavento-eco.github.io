<?php
/**
 * Barlavento landing page — server-side render of the three network streams.
 *
 * Exposed as the [bl_home] shortcode so it works inside the block theme's
 * front page. All markup and data-shaping live here in the theme (in files),
 * never in the database. The dynamic streams query live WP data, so anything
 * edited in wp-admin (an Offer/Want, a syndicated post) shows on next reload.
 */

if ( ! defined( 'ABSPATH' ) ) { exit; }

/** Map a member URL/email to a display name. */
function bl_home_member_name( $hint ) {
	$hint = strtolower( (string) $hint );
	if ( strpos( $hint, 'valedalama' ) !== false ) { return 'Quinta Vale da Lama'; }
	if ( strpos( $hint, 'mudvalley' ) !== false )  { return 'Mud Valley Foundation'; }
	if ( strpos( $hint, 'novasdescobertas' ) !== false ) { return 'Novas Descobertas'; }
	return 'Network member';
}

/**
 * The Directory — read LIVE from the Murmurations Index.
 *
 * Nothing here is typed into this site. We ask the Index which profiles carry
 * the barlavento-eco tag, then fetch each profile from wherever its member
 * keeps it. A member appears because they published, and disappears because
 * they stopped — neither is in our gift.
 *
 * Cached for 10 minutes (matching the profiles' own max-age). If the Index or
 * a member's host is unreachable we serve the last good result rather than an
 * empty Directory; only if we have never had one do we fall back to statics.
 */
define( 'BL_INDEX_QUERY', 'https://index.murmurations.network/v2/nodes?tags=barlavento-eco&tags_exact=true&status=posted&page_size=100&tags_filter=and' );

/** Growth stage, DERIVED: is the profile served from the member's own domain? */
function bl_home_stage_for( $profile_url, $primary_url ) {
	$ph = strtolower( (string) wp_parse_url( $profile_url, PHP_URL_HOST ) );
	$mh = strtolower( (string) wp_parse_url( $primary_url, PHP_URL_HOST ) );
	$ph = preg_replace( '/^www\./', '', $ph );
	$mh = preg_replace( '/^www\./', '', $mh );
	if ( $ph !== '' && $ph === $mh ) { return 'established'; }          // own domain
	if ( strpos( $ph, 'murmurmaps' ) !== false ) { return 'seedling'; }  // hosted for them
	return 'sapling';                                                    // own file, someone else's domain
}

function bl_home_orgs_fetch() {
	$res = wp_remote_get( BL_INDEX_QUERY, array( 'timeout' => 5 ) );
	if ( is_wp_error( $res ) || 200 !== wp_remote_retrieve_response_code( $res ) ) { return null; }
	$body = json_decode( wp_remote_retrieve_body( $res ), true );
	if ( empty( $body['data'] ) ) { return null; }

	$orgs = array();
	foreach ( $body['data'] as $node ) {
		$schemas = isset( $node['linked_schemas'] ) ? (array) $node['linked_schemas'] : array();
		if ( ! preg_grep( '/^organizations_schema/', $schemas ) ) { continue; }
		$purl = isset( $node['profile_url'] ) ? $node['profile_url'] : '';
		if ( ! $purl ) { continue; }

		$pr = wp_remote_get( $purl, array( 'timeout' => 5 ) );
		if ( is_wp_error( $pr ) || 200 !== wp_remote_retrieve_response_code( $pr ) ) { continue; }
		$p = json_decode( wp_remote_retrieve_body( $pr ), true );
		if ( empty( $p['name'] ) ) { continue; }

		// barlavento-eco is the membership test, not a descriptive tag — don't show it back.
		$tags = array_values( array_diff( (array) ( isset( $p['tags'] ) ? $p['tags'] : array() ), array( 'barlavento-eco' ) ) );

		$orgs[] = array(
			'name'  => $p['name'],
			'nick'  => ! empty( $p['nickname'] ) ? $p['nickname'] : $p['name'],
			'url'   => ! empty( $p['primary_url'] ) ? $p['primary_url'] : $purl,
			'stage' => bl_home_stage_for( $purl, isset( $p['primary_url'] ) ? $p['primary_url'] : '' ),
			'desc'  => isset( $p['description'] ) ? $p['description'] : '',
			'tags'  => array_slice( $tags, 0, 4 ),
			'rels'  => isset( $p['relationships'] ) ? count( (array) $p['relationships'] ) : 0,
		);
	}
	if ( ! $orgs ) { return null; }

	usort( $orgs, function( $a, $b ) { return $b['rels'] - $a['rels']; } );
	return $orgs;
}

function bl_home_orgs() {
	$cached = get_transient( 'bl_home_orgs_live' );
	if ( is_array( $cached ) && $cached ) { return $cached; }

	$live = bl_home_orgs_fetch();
	if ( $live ) {
		set_transient( 'bl_home_orgs_live', $live, 10 * MINUTE_IN_SECONDS );
		update_option( 'bl_home_orgs_lastgood', $live, false );
		return $live;
	}

	$last = get_option( 'bl_home_orgs_lastgood' );
	if ( is_array( $last ) && $last ) { return $last; }

	// Cold start with the network unreachable. Kept minimal and factual.
	return array(
		array( 'name'=>'Quinta Vale da Lama', 'nick'=>'VdL', 'url'=>'https://valedalama.net', 'stage'=>'established',
			'desc'=>'A regenerative organic farm in Odiáxere, SW Algarve — the hub of a Barlavento partner network.',
			'tags'=>array('regenerative agriculture','permaculture','agrotourism'), 'rels'=>3 ),
		array( 'name'=>'Mud Valley Foundation', 'nick'=>'MVF', 'url'=>'https://mudvalley.org', 'stage'=>'established',
			'desc'=>'Nonprofit for education and action-oriented ecosystem restoration in SW Portugal.',
			'tags'=>array('nonprofit','ecosystem restoration','bioregional'), 'rels'=>2 ),
		array( 'name'=>'Casa Vale da Lama', 'nick'=>'Casa', 'url'=>'https://casavaledalama.com', 'stage'=>'established',
			'desc'=>'A regenerative farm-stay eco resort at Quinta Vale da Lama — hospitality on a working organic farm.',
			'tags'=>array('eco resort','regenerative hospitality','farm stay'), 'rels'=>2 ),
		array( 'name'=>'Novas Descobertas Association', 'nick'=>'AND', 'url'=>'https://novasdescobertas.org', 'stage'=>'established',
			'desc'=>'Portuguese educational NGO at Quinta Vale da Lama — experiential, nature-connected learning.',
			'tags'=>array('education','NGO','youth'), 'rels'=>1 ),
	);
}

function bl_home_esc_tags( $tags ) {
	$out = '';
	foreach ( (array) $tags as $t ) {
		if ( $t === '' ) { continue; }
		$out .= '<span class="tag">' . esc_html( $t ) . '</span>';
	}
	return $out;
}

/** Growth-stage badge (charter ladder: Seedling → Sapling → Established). */
function bl_home_stage_badge( $stage ) {
	$map = array(
		'seedling'    => array( '🌱', 'Seedling',    'st-seedling',    'Hosted in the community nursery' ),
		'sapling'     => array( '🌿', 'Sapling',     'st-sapling',     'Own site on managed ground (WordPress.com, micro.blog…)' ),
		'established' => array( '🌳', 'Established',  'st-established',  'Own domain, fully sovereign presence' ),
	);
	$s = isset( $map[ $stage ] ) ? $map[ $stage ] : $map['established'];
	return '<span class="stage ' . $s[2] . '" title="Growth stage — ' . esc_attr( $s[3] ) . '">'
		. $s[0] . ' ' . esc_html( $s[1] ) . '</span>';
}

/** Directory card. */
function bl_home_card_org( $o ) {
	$rel = intval( $o['rels'] );
	return '<div class="card" data-kind="org">'
		. '<span class="kind k-org">◉ Directory · Profile</span>'
		. bl_home_stage_badge( isset( $o['stage'] ) ? $o['stage'] : 'established' )
		. '<h4>' . esc_html( $o['name'] ) . '</h4>'
		. '<div class="who">' . esc_html( $o['nick'] ) . ' · Murmurations profile</div>'
		. '<p class="desc">' . esc_html( $o['desc'] ) . '</p>'
		. '<div class="tags">' . bl_home_esc_tags( $o['tags'] ) . '</div>'
		. '<div class="rel">↔ ' . $rel . ' declared relationship' . ( $rel === 1 ? '' : 's' ) . '</div>'
		. '<a class="go" href="' . esc_url( $o['url'] ) . '" target="_blank" rel="noopener">Visit their site →</a>'
		. '</div>';
}

/** Offers & Wants cards, live from the offer_want CPT. */
function bl_home_cards_exchange() {
	$q = new WP_Query( array(
		'post_type'      => 'offer_want',
		'post_status'    => 'publish',
		'posts_per_page' => 12,
		'orderby'        => 'date',
		'order'          => 'DESC',
	) );
	if ( ! $q->have_posts() ) { return '<div class="empty" data-kind="offer">No offers or wants published yet.</div>'; }
	$out = '';
	while ( $q->have_posts() ) {
		$q->the_post();
		$id   = get_the_ID();
		$ex   = strtolower( (string) get_post_meta( $id, 'ow_exchange_type', true ) );
		$kind = ( $ex === 'want' ) ? 'want' : 'offer';
		$item = (string) get_post_meta( $id, 'ow_item_type', true );
		$scope= (string) get_post_meta( $id, 'ow_geographic_scope', true );
		$desc = (string) get_post_meta( $id, 'ow_description', true );
		$url  = (string) get_post_meta( $id, 'ow_details_url', true );
		$email= (string) get_post_meta( $id, 'ow_contact_email', true );
		$who  = bl_home_member_name( $url !== '' ? $url : $email );
		$cls  = ( $kind === 'want' ) ? 'k-want' : 'k-offer';
		$ic   = ( $kind === 'want' ) ? '↘' : '↗';
		$label= ( $kind === 'want' ) ? 'Want' : 'Offer';
		$link = $url !== '' ? $url : ( $email !== '' ? 'mailto:' . $email : '' );
		$tags = array_filter( array( $item, $scope ) );
		$out .= '<div class="card" data-kind="' . esc_attr( $kind ) . '">'
			. '<span class="kind ' . $cls . '">' . $ic . ' ' . $label . ( $item ? ' · ' . esc_html( $item ) : '' ) . '</span>'
			. '<h4>' . esc_html( get_the_title() ) . '</h4>'
			. '<div class="who">' . esc_html( $who ) . '</div>'
			. '<p class="desc">' . esc_html( wp_trim_words( $desc, 34 ) ) . '</p>'
			. '<div class="tags">' . bl_home_esc_tags( $tags ) . '</div>'
			. ( $link ? '<a class="go" href="' . esc_url( $link ) . '" target="_blank" rel="noopener">Details →</a>' : '' )
			. '</div>';
	}
	wp_reset_postdata();
	return $out;
}

/** River cards — recent posts (the syndicated journal). */
function bl_home_cards_river() {
	// The River is the syndicated partner feeds (FeedWordPress), identified by
	// the syndication_source meta — so it shows real member content with real
	// attribution, distinct from any native posts on the sandbox.
	$q = new WP_Query( array(
		'post_type'      => 'post',
		'post_status'    => 'publish',
		'posts_per_page' => 6,
		'ignore_sticky_posts' => true,
		'meta_query'     => array( array( 'key' => 'syndication_source', 'compare' => 'EXISTS' ) ),
	) );
	if ( ! $q->have_posts() ) { return '<div class="empty" data-kind="news">No journal posts yet.</div>'; }
	$out = '';
	while ( $q->have_posts() ) {
		$q->the_post();
		// Real source comes from FeedWordPress syndication meta once feeds are
		// wired; native posts have none, so fall back to a plain "Journal".
		$src = (string) get_post_meta( get_the_ID(), 'syndication_source', true );
		$src = html_entity_decode( $src, ENT_QUOTES );
		$src = preg_replace( '/\s*[-–—]?\s*Events?\s*RSS feed\s*$/i', '', $src ); // tidy feed titles
		$src = trim( preg_replace( '/\s*RSS feed\s*$/i', '', $src ) );
		$label = $src !== '' ? 'Journal · ' . esc_html( $src ) : 'Journal';
		$out .= '<div class="card news" data-kind="news">'
			. '<span class="kind k-news">❋ ' . $label . '</span>'
			. '<h4>' . esc_html( get_the_title() ) . '</h4>'
			. '<div class="who">' . esc_html( get_the_date( 'j M Y' ) ) . '</div>'
			. '<p class="desc">' . esc_html( wp_trim_words( wp_strip_all_tags( get_the_excerpt() ), 28 ) ) . '</p>'
			. '<a class="go" href="' . esc_url( get_permalink() ) . '">Read →</a>'
			. '</div>';
	}
	wp_reset_postdata();
	return $out;
}

/** The whole landing page. */
function bl_home_shortcode() {
	$orgs = '';
	foreach ( bl_home_orgs() as $o ) { $orgs .= bl_home_card_org( $o ); }
	$exchange = bl_home_cards_exchange();
	$river    = bl_home_cards_river();
	$thumb    = '/wp-content/uploads/network-home/img';

	ob_start(); ?>
<div class="bl-home">
  <section class="hero"><div class="wrap">
    <div class="eyebrow">Ecosystem Regeneration Community of the Barlavento</div>
    <h1>A diverse and inclusive network of people and organisations rooted in relationship with the living world. Together, we work to create impactful watershed-scale regeneration of <em>our living ecosystems</em>.</h1>
    <div class="sig">— Statement of Identity &amp; Purpose, agreed June 2026</div>
  </div></section>

  <section class="sec"><div class="wrap">
    <div class="sec-head"><h2>See the network</h2><p>Two ways to look at ourselves — as a web of relationships, and as a territory.</p></div>
    <div class="maps">
      <a class="mapcard" href="/ercb-community/">
        <img src="<?php echo esc_attr( $thumb ); ?>/thumb-community.png" alt="Social system map"/>
        <div class="body"><h3>Who we are to each other</h3><p>The community as a living web of working relationships — who collaborates with whom.</p><div class="go">Open the social map →</div></div>
      </a>
      <a class="mapcard" href="/ercb-projects/">
        <img src="<?php echo esc_attr( $thumb ); ?>/thumb-projects.png" alt="Projects map"/>
        <div class="body"><h3>Where we are on the land</h3><p>The participating projects placed on the territory they are restoring, across the watershed.</p><div class="go">Open the projects map →</div></div>
      </a>
    </div>
  </div></section>

  <section class="sec" id="network"><div class="wrap">
    <div class="sec-head"><h2>Fresh from the network</h2><p>Everything below flows from data members publish and control on their own sites — profiles, offers &amp; wants, and news. We aggregate; we never enclose.</p></div>
    <div class="tabs" id="bl-tabs">
      <button class="tab on" data-f="all">All</button>
      <button class="tab" data-f="org">Directory</button>
      <button class="tab" data-f="exchange">Offers &amp; Wants</button>
      <button class="tab" data-f="news">Journal</button>
    </div>
    <div class="feed" id="bl-feed" data-filter="all"><?php echo $exchange . $orgs . $river; // phpcs:ignore ?></div>
    <div class="ladder">
      <span class="ladder-lead">Every member is met where they are and helped to grow:</span>
      <span class="stage st-seedling">🌱 Seedling</span><span class="ladder-def">a page in the community nursery — we host it, you can take it anytime</span>
      <span class="stage st-sapling">🌿 Sapling</span><span class="ladder-def">your own site on managed ground (WordPress.com, micro.blog…)</span>
      <span class="stage st-established">🌳 Established</span><span class="ladder-def">your own domain — a fully sovereign presence</span>
    </div>
    <span class="note">Directory profiles carry a growth-stage badge (above). Offers &amp; Wants render live from the WordPress <em>Offers &amp; Wants</em> editor; the Journal renders from syndicated posts; profiles follow the Murmurations schema. Edit any of them in wp-admin and reload. <a href="/ercb-network-live/">See the network map, live &rarr;</a></span>
  </div></section>
</div>
<script>
(function(){
  var feed=document.getElementById('bl-feed'), tabs=document.getElementById('bl-tabs');
  if(!feed||!tabs) return;
  function match(f,k){return f==='all'||(f==='exchange'?(k==='offer'||k==='want'):f===k);}
  tabs.addEventListener('click',function(e){
    var b=e.target.closest('.tab'); if(!b) return;
    var f=b.dataset.f;
    tabs.querySelectorAll('.tab').forEach(function(t){t.classList.toggle('on',t===b);});
    feed.setAttribute('data-filter', f);
    feed.querySelectorAll('[data-kind]').forEach(function(c){c.style.display=match(f,c.dataset.kind)?'':'none';});
  });
})();
</script>
<?php
	return ob_get_clean();
}
add_shortcode( 'bl_home', 'bl_home_shortcode' );
