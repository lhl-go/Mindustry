package tiangong;
import arc.*;
import arc.files.Fi;
import arc.graphics.*;
import arc.graphics.g2d.*;
import arc.graphics.g2d.TextureAtlas.AtlasRegion;
import arc.struct.*;
import arc.util.Log;
import mindustry.Vars;
import mindustry.ctype.*;
import mindustry.game.EventType.ClientLoadEvent;
import mindustry.graphics.MultiPacker;
import mindustry.mod.Mod;
/** Art-only integration. Regenerates derived icons after original content initialization. */
public class BrandMod extends Mod {
    private final ObjectMap<String,PixmapRegion> pixels=new ObjectMap<>();
    @Override public void packSprites(MultiPacker ignored){
        for(AtlasRegion r:Core.atlas.getRegions())pixels.put(r.name,new PixmapRegion(Core.atlas.getPixmap(r).crop()));
        Fi root=Vars.mods.getMod(BrandMod.class).root;
        root.child("sprites-override").walk(file->{if(!file.extEquals("png"))return;String name=file.nameWithoutExtension();Pixmap p=new Pixmap(file);if(name.endsWith(".9")){name=name.substring(0,name.length()-2);Pixmap q=p.crop(1,1,p.width-2,p.height-2);p.dispose();p=q;}PixmapRegion old=pixels.put(name,new PixmapRegion(p));if(old!=null)old.pixmap.dispose();});
        root.child("extra-regions").walk(file->{if(file.extEquals("png")){Pixmap p=new Pixmap(file);String name=file.nameWithoutExtension();PixmapRegion old=pixels.put(name,new PixmapRegion(p));if(old!=null)old.pixmap.dispose();ignored.add(MultiPacker.PageType.main,name,p);}});
    }
    @Override public void init(){
        TextureAtlas live=Core.atlas;MultiPacker generated=new MultiPacker();
        TextureAtlas cpu=new TextureAtlas(){
            {error=live.find("error");}
            @Override public AtlasRegion find(String name){return live.find(name);}
            @Override public boolean has(String name){return live.has(name);}
            @Override public boolean isFound(TextureRegion region){return live.isFound(region);}
            @Override public PixmapRegion getPixmap(AtlasRegion r){PixmapRegion p=pixels.get(r.name);return p==null?pixels.get("error"):p;}
        };
        try{
            Core.atlas=cpu;
            for(var group:Vars.content.getContentMap())for(Content c:group)if(c instanceof UnlockableContent u && u.minfo.mod==null && !(u instanceof mindustry.world.Block b && (b.isFloor()||b.getClass().getPackageName().contains("environment"))))u.createIcons(generated);
        }finally{Core.atlas=live;}
        TextureAtlas icons=generated.flush(Texture.TextureFilter.linear,new TextureAtlas());
        int count=0;for(AtlasRegion r:icons.getRegions()){live.addRegion(r.name,r);count++;}
        live.getTextures().addAll(icons.getTextures());
        for(var group:Vars.content.getContentMap())for(Content c:group)if(c instanceof UnlockableContent u){u.load();u.loadIcon();}
        generated.dispose();for(var entry:pixels)entry.value.pixmap.dispose();pixels.clear();
        // The upstream main menu deliberately uses flat monochrome buttons. Apply the approved jade skin.
        mindustry.ui.Styles.flatToggleMenut.up=Core.atlas.drawable("button");
        mindustry.ui.Styles.flatToggleMenut.over=Core.atlas.drawable("button-over");
        mindustry.ui.Styles.flatToggleMenut.down=Core.atlas.drawable("button-down");
        mindustry.ui.Styles.flatToggleMenut.checked=Core.atlas.drawable("button-down");
        Log.info("[Tiangong] Regenerated @ content icon/layer regions from accepted art.",count);
    }
    public BrandMod(){Events.on(ClientLoadEvent.class,event->{Core.graphics.setTitle("天工仙阵");Core.app.post(()->{arc.scene.Element element=Vars.ui.menuGroup.find("buttons");if(element instanceof arc.scene.ui.layout.Table table)table.setBackground(Core.atlas.drawable("pane"));});});}
}
