/**
 * The region map shown from the title screen: every outdoor place, where it sits on a stylised map of Bengaluru,
 * and the real place behind it. Order follows the story.
 */

/** @typedef {{id: string, name: string, x: number, y: number, kind: 'home'|'town'|'route'|'park'|'lake'|'hill'|'landmark'|'wild', blurb: string, arena?: string}} RegionPlace */

/** @type {RegionPlace[]} */
export const REGION = [
  { id: 'basavanagudi', name: 'Basavanagudi', x: 200, y: 505, kind: 'home',
    blurb: "One of the city's oldest neighbourhoods: the Bull Temple, Bugle Rock with Kempegowda's watchtower, and the yearly groundnut fair. Your home town." },
  { id: 'route1', name: 'South End Road', x: 228, y: 462, kind: 'route',
    blurb: 'The leafy road from Basavanagudi up to Lalbagh, and your first tall grass.' },
  { id: 'lalbagh', name: 'Lalbagh', x: 262, y: 418, kind: 'park', arena: 'Hoovamma (GRASS) in the Glass House',
    blurb: 'The 240-acre botanical garden from the 1760s, famous for its Glass House flower shows and a rock 3,000 million years old.' },
  { id: 'cubbon_park', name: 'Cubbon Park', x: 300, y: 352, kind: 'park',
    blurb: "The green heart of the city: bamboo groves, a bandstand, morning walkers and fruit bats. The Concrete Syndicate first shows up here." },
  { id: 'mg_road', name: 'MG Road', x: 352, y: 338, kind: 'town', arena: 'Gundappa (FIGHT) at Chinnaswamy Stadium',
    blurb: "Mahatma Gandhi Road, the city's busiest boulevard, with Namma Metro overhead and the cricket stadium next door." },
  { id: 'silk_board', name: 'Silk Board Junction', x: 365, y: 440, kind: 'route',
    blurb: 'The junction famous across India for its traffic jams. Signals here last long enough to evolve.' },
  { id: 'whitefield', name: 'Whitefield', x: 472, y: 318, kind: 'town', arena: 'Tanvi (ELECTRIC) at the tech park',
    blurb: 'The tech corridor: glass towers, startup demo days and two-hour commutes.' },
  { id: 'bellandur', name: 'Bellandur Lake', x: 440, y: 420, kind: 'lake',
    blurb: 'A huge lake known for the toxic foam that drifted onto roads, and for the day it caught fire.' },
  { id: 'sankey_tank', name: 'Sankey Tank', x: 182, y: 258, kind: 'lake',
    blurb: 'A 19th-century reservoir loved by joggers, fireflies and dragonflies.' },
  { id: 'malleshwaram', name: 'Malleshwaram', x: 150, y: 305, kind: 'town', arena: 'Vidya (MIND) at her tuition house',
    blurb: 'An old neighbourhood of temples, jasmine sellers, rangoli and tiled-roof homes.' },
  { id: 'palace_road', name: 'Palace Road', x: 252, y: 268, kind: 'landmark', arena: 'Rukmini (SPIRIT) in Bangalore Palace',
    blurb: 'Bangalore Palace, built in a Tudor style in 1878, its corridors said to be restless at night.' },
  { id: 'hebbal', name: 'Hebbal', x: 285, y: 205, kind: 'lake',
    blurb: 'The lake and the famous flyover on the road north to the hills. Pelicans and storks feed here.' },
  { id: 'nandi_hills', name: 'Nandi Hills', x: 272, y: 122, kind: 'hill', arena: 'Akash (SKY) at the hill pavilion',
    blurb: "The hill fortress north of the city, where everyone drives at dawn to watch the sun rise over the clouds." },
  { id: 'vidhana_soudha', name: 'Vidhana Soudha', x: 262, y: 322, kind: 'landmark',
    blurb: "The granite seat of Karnataka's legislature, with the state emblem over its doors. The Namma Council waits inside." },
  { id: 'bannerghatta', name: 'Bannerghatta Forest', x: 292, y: 545, kind: 'wild',
    blurb: 'The forest on the southern edge of the city, home to elephants, leopards and a national park.' },
  { id: 'ramanagara', name: 'Ramanagara Rocks', x: 110, y: 520, kind: 'hill',
    blurb: 'Giant granite boulder hills south-west of the city, where vultures nest on the cliffs. Open after becoming Champion.' },
  { id: 'kokkare_bellur', name: 'Kokkare Bellur', x: 52, y: 468, kind: 'wild',
    blurb: 'A village where painted storks and pelicans nest on rooftop trees every winter, protected by the villagers.' },
];

/** Roads drawn between places. */
export const REGION_ROADS = [
  ['basavanagudi', 'route1'], ['route1', 'lalbagh'], ['lalbagh', 'cubbon_park'], ['cubbon_park', 'mg_road'],
  ['mg_road', 'silk_board'], ['silk_board', 'whitefield'], ['whitefield', 'bellandur'], ['mg_road', 'vidhana_soudha'],
  ['vidhana_soudha', 'sankey_tank'], ['sankey_tank', 'malleshwaram'], ['malleshwaram', 'palace_road'],
  ['palace_road', 'hebbal'], ['hebbal', 'nandi_hills'], ['basavanagudi', 'bannerghatta'], ['basavanagudi', 'ramanagara'],
  ['ramanagara', 'kokkare_bellur'],
];
