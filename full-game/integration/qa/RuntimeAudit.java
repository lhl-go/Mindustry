package tiangong.qa;
import arc.*;
import arc.files.Fi;
import arc.graphics.Color;
import arc.graphics.g2d.*;
import arc.struct.*;
import arc.util.*;
import arc.util.serialization.*;
import mindustry.*;
import mindustry.content.*;
import mindustry.core.GameState.State;
import mindustry.game.*;
import mindustry.gen.*;
import mindustry.mod.Mod;
import mindustry.type.*;
import mindustry.world.*;
import mindustry.world.blocks.environment.Floor;
import mindustry.world.meta.Env;
import mindustry.world.blocks.defense.turrets.Turret;
import mindustry.world.blocks.production.GenericCrafter;
import mindustry.world.blocks.defense.Door;
import static mindustry.Vars.*;
/** Automated real OpenGL client acceptance; isolated test mod, never shipped in production mod. */
public class RuntimeAudit extends Mod {
    Fi output=new Fi(System.getProperty("tiangong.audit.out"));
    Seq<String> captures=new Seq<>(), failures=new Seq<>(), regionChecks=new Seq<>();
    Seq<Block> blocks=new Seq<>(); Seq<UnitType> units=new Seq<>();
    int stage=0,frames=0,page=0,atlasResourcesChecked=0; boolean loaded=false; float cx=400,cy=400;
    public RuntimeAudit(){
        Events.on(EventType.ClientLoadEvent.class,e->{
            loaded=true;output.mkdirs();
            Core.settings.put("locale","zh_CN"); Core.settings.put("lasthost","127.0.0.1");
            Core.settings.put("fpscap",60); Core.settings.put("modcrashdisable",false);
            var art=mods.locateMod("tiangong-xianzhen-art");
            for(String folder:new String[]{"sprites-override","extra-regions"})art.root.child(folder).walk(file->{if(!file.extEquals("png"))return;String name=file.nameWithoutExtension();if(name.endsWith(".9"))name=name.substring(0,name.length()-2);atlasResourcesChecked++;if(!Core.atlas.has(name))failures.add("Unresolved module region "+name);});
            for(Block b:content.blocks())if(!b.isAir()&&b.region!=null&&b.region.found())blocks.add(b);
            for(UnitType u:content.units())if(!u.internal&&u.region!=null&&u.region.found())units.add(u);
            Core.app.addListener(new ApplicationListener(){public void update(){tick();}});
        });
    }
    void hide(){for(arc.scene.Element e:Core.scene.root.getChildren().copy())if(e instanceof arc.scene.ui.Dialog d)d.hide();}
    void shot(String name){Core.app.post(()->{try{ScreenUtils.saveScreenshot(output.child(name+".png"));captures.add(name);Log.info("ART_CAPTURE @",name);}catch(Throwable t){failures.add(name+":"+t);}});}
    void tick(){if(!loaded)return;try{
        frames++;
        if(state.isGame()){player.set(cx,cy);Core.camera.position.set(cx,cy);renderer.setScale(2f);}
        if(stage==0&&frames==120){hide();}
        if(stage==0&&frames==180){shot("01-menu");stage=1;frames=0;ui.settings.show();}
        else if(stage==1&&frames==90){shot("02-settings");hide();stage=2;frames=0;makeWorld(false,0);}
        else if(stage==2&&(frames==80||frames==120)){shot(String.format("blocks-%02d-%03d",page,frames));if(frames==120){page++;frames=0;if(page*24<blocks.size)makeWorld(false,page);else{page=0;stage=3;makeWorld(true,0);}}}
        else if(stage==3&&(frames==80||frames==120)){shot(String.format("units-%02d-%03d",page,frames));if(frames==120){page++;frames=0;if(page*20<units.size)makeWorld(true,page);else{stage=4;frames=0;dynamicWorld();}}}
        else if(stage==4){
            for(Building b:Groups.build){if(b.power!=null)b.power.status=1;if(b instanceof GenericCrafter.GenericCrafterBuild g){g.warmup=1;g.totalProgress+=1;g.progress=(frames%60)/60f;}if(b instanceof Turret.TurretBuild t){t.rotation=frames*2f;t.heat=.75f;t.recoilOffset.trns(t.rotation,2f);}if(b instanceof Door.DoorBuild d)d.open=frames>120;}
            if(frames%30==0){mindustry.entities.Puddles.deposit(world.tile(50,50),Liquids.water,60);Fx.fire.at(420,360);Fx.explosion.at(455,400);Fx.smoke.at(380,420);}
            if(frames==80||frames==160||frames==240)shot("dynamic-"+frames);
            if(frames==270){writeResult();Core.app.exit();}
        }
    }catch(Throwable t){failures.add(t.toString());Log.err(t);writeResult();Core.app.exit();}}
    void makeWorld(boolean unitPage,int index){
        logic.reset();state.rules=new Rules();state.rules.infiniteResources=true;state.rules.waves=false;state.rules.canGameOver=false;state.rules.editor=true;state.rules.disableUnitCap=true;state.rules.env=Env.terrestrial;
        world.loadGenerator(100,100,tiles->{for(int x=0;x<100;x++)for(int y=0;y<100;y++)tiles.set(x,y,new Tile(x,y,Blocks.stone,Blocks.air,Blocks.air));
            tiles.get(5,5).setBlock(Blocks.coreShard,Team.sharded);
            if(!unitPage){for(int i=0;i<24&&index*24+i<blocks.size;i++){Block b=blocks.get(index*24+i);int x=22+(i%6)*11,y=28+(i/6)*13;Tile tile=tiles.get(x,y);if(b instanceof Floor floor){for(int dx=-3;dx<=3;dx++)for(int dy=-3;dy<=3;dy++)tiles.get(x+dx,y+dy).setFloor(floor);}else{tile.setBlock(b,Team.sharded,i%4);}}}
        });
        logic.play();state.rules.canGameOver=false;state.rules.editor=true;state.set(State.playing);
        player.team(Team.sharded);player.set(cx,cy);ui.hudfrag.shown=!unitPage;
        for(Building b:Groups.build){b.enabled=true;if(b.items!=null)for(Item item:content.items())b.items.set(item,Math.min(50,b.block.itemCapacity));if(b.liquids!=null)b.liquids.add(Liquids.water,b.block.liquidCapacity/2);if(b.power!=null){b.power.status=1;b.power.graph.add(b);}}
        if(unitPage){for(int i=0;i<20&&index*20+i<units.size;i++){UnitType u=units.get(index*20+i);Unit unit=u.create(Team.sharded);unit.set((22+i%5*14)*8,(28+i/5*13)*8);unit.rotation=i%4*90;unit.add();}}
        for(String name:new String[]{"conveyor-0-0","mechanical-drill","duo","dagger","logo","colored-floor-0","metal-tiles-11-1-46"}){if(!Core.atlas.has(name))failures.add("Missing atlas region "+name);else regionChecks.add(name);}
    }
    void dynamicWorld(){makeWorld(false,8);for(int x=25;x<70;x++){world.tile(x,42).setBlock(Blocks.conveyor,Team.sharded,0);world.tile(x,46).setBlock(Blocks.conduit,Team.sharded,0);}for(int x:new int[]{30,40,50,60})world.tile(x,57).setBlock(Blocks.door,Team.sharded);for(int x:new int[]{30,45,60})world.tile(x,35).setBlock(Blocks.duo,Team.sharded);for(Building b:Groups.build){if(b.liquids!=null)b.liquids.add(Liquids.water,b.block.liquidCapacity*.7f);if(b.items!=null)b.items.clear();}for(int x=25;x<70;x+=2)world.tile(x,42).build.handleStack(Items.copper,1,null);}
    public static class Report{public String clientVersion,openGL;public int renderedBlocks,renderedUnitTypes,atlasResourcesChecked;public Seq<String> captures,failures,regionChecks;public boolean productionModLoaded;}
    void writeResult(){Json j=new Json();j.setTypeName(null);j.setOutputType(JsonWriter.OutputType.json);Report r=new Report();r.clientVersion=mindustry.core.Version.combined();r.openGL=Core.graphics.getGLVersion().toString();r.renderedBlocks=blocks.size;r.renderedUnitTypes=units.size;r.atlasResourcesChecked=atlasResourcesChecked;r.captures=captures;r.failures=failures;r.regionChecks=regionChecks;r.productionModLoaded=mods.locateMod("tiangong-xianzhen-art")!=null;output.child("runtime-result.json").writeString(j.prettyPrint(r));}
}
