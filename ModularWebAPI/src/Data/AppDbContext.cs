using Microsoft.EntityFrameworkCore;
using ModularWebAPI.Auth.Do;
using ModularWebAPI.Users.Do;

namespace ModularWebAPI.Data
{
    public class AppDbContext : DbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
        {
        }

        // Auth
        public DbSet<User> Users { get; set; }
        public DbSet<Fournisseur> Fournisseurs { get; set; }
        public DbSet<Article> Articles { get; set; }
        public DbSet<Commande> Commandes { get; set; }
        public DbSet<LigneCommande> LignesCommande { get; set; }
        public DbSet<Alerte> Alertes { get; set; }
        public DbSet<MouvementStock> MouvementsStock { get; set; }
        public DbSet<PrevisionConsommation> PrevisionsConsommation { get; set; }
        public DbSet<CalculCouverture> CalculsCouverture { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            // Configure User
            modelBuilder.Entity<User>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.Id).ValueGeneratedOnAdd();
                entity.Property(e => e.Email).IsRequired().HasMaxLength(255);
                entity.Property(e => e.Nom).IsRequired().HasMaxLength(100);
                entity.Property(e => e.Prenom).IsRequired().HasMaxLength(100);
                entity.Property(e => e.Role).IsRequired().HasConversion<string>();
                entity.Property(e => e.CreatedAt).HasDefaultValueSql("GETUTCDATE()");
                entity.HasIndex(e => e.Email).IsUnique();
            });

            // Configure Fournisseur
            modelBuilder.Entity<Fournisseur>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.Id).ValueGeneratedOnAdd();
                entity.Property(e => e.Nom).IsRequired().HasMaxLength(200);
                entity.Property(e => e.CodeFournisseur).IsRequired().HasMaxLength(50);
                entity.Property(e => e.CreatedAt).HasDefaultValueSql("GETUTCDATE()");
                entity.Property(e => e.UpdatedAt).HasDefaultValueSql("GETUTCDATE()");
                entity.HasIndex(e => e.CodeFournisseur).IsUnique();
            });

            // Configure Article
            modelBuilder.Entity<Article>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.Id).ValueGeneratedOnAdd();
                entity.Property(e => e.Reference).IsRequired().HasMaxLength(50);
                entity.Property(e => e.Nom).IsRequired().HasMaxLength(200);
                entity.Property(e => e.PrixUnitaire).HasColumnType("decimal(10,2)");
                entity.Property(e => e.CreatedAt).HasDefaultValueSql("GETUTCDATE()");
                entity.Property(e => e.UpdatedAt).HasDefaultValueSql("GETUTCDATE()");
                entity.HasIndex(e => e.Reference).IsUnique();
                entity.HasOne<Fournisseur>()
                      .WithMany()
                      .HasForeignKey(e => e.FournisseurId)
                      .OnDelete(DeleteBehavior.Restrict);
            });

            // Configure Commande
            modelBuilder.Entity<Commande>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.Id).ValueGeneratedOnAdd();
                entity.Property(e => e.NumeroCommande).IsRequired().HasMaxLength(50);
                entity.Property(e => e.Status).IsRequired().HasConversion<string>();
                entity.Property(e => e.TotalHt).HasColumnType("decimal(10,2)");
                entity.Property(e => e.TotalTtc).HasColumnType("decimal(10,2)");
                entity.Property(e => e.TauxTva).HasColumnType("decimal(5,2)");
                entity.Property(e => e.CreatedAt).HasDefaultValueSql("GETUTCDATE()");
                entity.Property(e => e.UpdatedAt).HasDefaultValueSql("GETUTCDATE()");
                entity.HasIndex(e => e.NumeroCommande).IsUnique();
                entity.HasOne<Fournisseur>()
                      .WithMany()
                      .HasForeignKey(e => e.FournisseurId)
                      .OnDelete(DeleteBehavior.Restrict);
                entity.HasOne<User>()
                      .WithMany()
                      .HasForeignKey(e => e.CreatedBy)
                      .OnDelete(DeleteBehavior.Restrict);
            });

            // Configure LigneCommande
            modelBuilder.Entity<LigneCommande>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.Id).ValueGeneratedOnAdd();
                entity.Property(e => e.PrixUnitaire).HasColumnType("decimal(10,2)");
                entity.Property(e => e.Total).HasColumnType("decimal(10,2)");
                entity.HasOne<Commande>()
                      .WithMany(c => c.Lignes)
                      .HasForeignKey(e => e.CommandeId)
                      .OnDelete(DeleteBehavior.Cascade);
                entity.HasOne<Article>()
                      .WithMany()
                      .HasForeignKey(e => e.ArticleId)
                      .OnDelete(DeleteBehavior.Restrict);
            });

            // Configure Alerte
            modelBuilder.Entity<Alerte>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.Id).ValueGeneratedOnAdd();
                entity.Property(e => e.Type).IsRequired().HasConversion<string>();
                entity.Property(e => e.Priorite).IsRequired().HasConversion<string>();
                entity.Property(e => e.Titre).IsRequired().HasMaxLength(200);
                entity.Property(e => e.CreatedAt).HasDefaultValueSql("GETUTCDATE()");
            });

            // Configure MouvementStock
            modelBuilder.Entity<MouvementStock>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.Id).ValueGeneratedOnAdd();
                entity.Property(e => e.TypeMouvement).IsRequired().HasConversion<string>();
                entity.Property(e => e.DateMouvement).HasDefaultValueSql("GETUTCDATE()");
                entity.Property(e => e.CreatedAt).HasDefaultValueSql("GETUTCDATE()");
                entity.HasOne<Article>()
                      .WithMany()
                      .HasForeignKey(e => e.ArticleId)
                      .OnDelete(DeleteBehavior.Restrict);
                entity.HasOne<User>()
                      .WithMany()
                      .HasForeignKey(e => e.CreatedBy)
                      .OnDelete(DeleteBehavior.Restrict);
            });

            // Configure PrevisionConsommation
            modelBuilder.Entity<PrevisionConsommation>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.Id).ValueGeneratedOnAdd();
                entity.Property(e => e.QuantitePrevue).HasColumnType("decimal(10,2)");
                entity.Property(e => e.QuantiteReelle).HasColumnType("decimal(10,2)");
                entity.Property(e => e.EcartAbsolu).HasColumnType("decimal(10,2)");
                entity.Property(e => e.EcartRelatif).HasColumnType("decimal(5,2)");
                entity.Property(e => e.CreatedAt).HasDefaultValueSql("GETUTCDATE()");
                entity.Property(e => e.UpdatedAt).HasDefaultValueSql("GETUTCDATE()");
                entity.HasOne<Article>()
                      .WithMany()
                      .HasForeignKey(e => e.ArticleId)
                      .OnDelete(DeleteBehavior.Restrict);
            });

            // Configure CalculCouverture
            modelBuilder.Entity<CalculCouverture>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.Id).ValueGeneratedOnAdd();
                entity.Property(e => e.Cms).HasColumnType("decimal(10,2)");
                entity.Property(e => e.Cmc).HasColumnType("decimal(10,2)");
                entity.Property(e => e.Qm).HasColumnType("decimal(10,2)");
                entity.Property(e => e.Cr).HasColumnType("decimal(10,2)");
                entity.Property(e => e.CouvertureActuelle).HasColumnType("decimal(10,2)");
                entity.Property(e => e.CreatedAt).HasDefaultValueSql("GETUTCDATE()");
                entity.HasOne<Article>()
                      .WithMany()
                      .HasForeignKey(e => e.ArticleId)
                      .OnDelete(DeleteBehavior.Restrict);
            });
        }
    }
}