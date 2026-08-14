import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

const CHARACTERS_INFO = [
  { key: "doraemon", displayName: "Doraemon", series: "Doraemon", role: "Cat Robot", color: "#00a0e9", bio: "A earless robotic cat from the 22nd century who travels back in time to help Nobita Nobi with his futuristic gadgets." },
  { key: "nobi_nobita", displayName: "Nobita Nobi", series: "Doraemon", role: "Main Character", color: "#f7b500", bio: "A lazy, clumsy, but kind-hearted 4th grader who relies on Doraemon's secret gadgets." },
  { key: "shizuka_minamoto", displayName: "Shizuka Minamoto", series: "Doraemon", role: "Friend & Future Wife", color: "#ff80ab", bio: "A sweet, intelligent, and studious girl who loves violin, baths, and baked sweet potatoes." },
  { key: "takeshi_goda_gian", displayName: "Takeshi 'Gian' Goda", series: "Doraemon", role: "Neighborhood Bully", color: "#ff6f00", bio: "Strong and short-tempered, Gian loves singing (terribly) and playing baseball." },
  { key: "suneo_honekawa", displayName: "Suneo Honekawa", series: "Doraemon", role: "Wealthy Friend", color: "#4caf50", bio: "A fox-faced rich kid who brags about expensive toys and pets." },
  { key: "dorami", displayName: "Dorami", series: "Doraemon", role: "Younger Sister", color: "#fff176", bio: "Doraemon's younger yellow cat robot sister who is smarter and more responsible." },
  { key: "shinnosuke_nohara", displayName: "Shinnosuke 'Shin-chan' Nohara", series: "Shin-chan", role: "Protagonist", color: "#e53935", bio: "A mischievous, shameless 5-year-old boy who loves Chocobi snacks and Action Kamen." },
  { key: "misae_nohara", displayName: "Misae Nohara", series: "Shin-chan", role: "Mother", color: "#ab47bc", bio: "Shin-chan's homemaker mother known for her fist-twisting punishment and bargain shopping." },
  { key: "hiroshi_nohara", displayName: "Hiroshi Nohara", series: "Shin-chan", role: "Father", color: "#0288d1", bio: "Shin-chan's hardworking salaryman father who loves beer and has notorious smelly feet." },
  { key: "himawari_nohara", displayName: "Himawari Nohara", series: "Shin-chan", role: "Baby Sister", color: "#ffd54f", bio: "Shin-chan's baby sister who loves shiny jewelry and handsome young men." },
  { key: "shiro_dog", displayName: "Shiro", series: "Shin-chan", role: "Pet Dog", color: "#eceff1", bio: "The Nohara family's intelligent white fluffy dog who often takes care of himself." },
  { key: "toru_kazama", displayName: "Toru Kazama", series: "Shin-chan", role: "Smart Friend", color: "#1e88e5", bio: "Shin-chan's elite, polite kindergarten classmate who secretly loves Moe-P anime." },
  { key: "nene_sakurada", displayName: "Nene Sakurada", series: "Shin-chan", role: "Fiery Friend", color: "#ec407a", bio: "A cute kindergarten girl who vents her rage on a stuffed bunny rabbit." },
  { key: "masao_sato", displayName: "Masao Sato", series: "Shin-chan", role: "Timid Friend", color: "#26a69a", bio: "An easily frightened, crying kindergarten boy with an onion-shaped head." },
  { key: "bo_chan", displayName: "Bo-chan", series: "Shin-chan", role: "Calm Friend", color: "#8d6e63", bio: "A quiet, slow-talking boy who constantly has a runny nose and loves collecting unique stones." }
];

async function main() {
  console.log("Start seeding...");
  for (const c of CHARACTERS_INFO) {
    const char = await prisma.character.upsert({
      where: { key: c.key },
      update: c,
      create: c,
    });
    console.log(`Created character: ${char.displayName}`);
  }
  console.log("Seeding finished.");
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
