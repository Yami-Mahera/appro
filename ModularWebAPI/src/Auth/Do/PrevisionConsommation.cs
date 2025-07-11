using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace ModularWebAPI.Auth.Do
{
    public class PrevisionConsommation
    {
        [Key]
        public Guid Id { get; set; } = Guid.NewGuid();
        
        [Required]
        public Guid ArticleId { get; set; }
        
        [Required]
        public int Semaine { get; set; }
        
        [Required]
        public int Annee { get; set; }
        
        [Required]
        public DateTime DateDebutSemaine { get; set; }
        
        [Required]
        public DateTime DateFinSemaine { get; set; }
        
        [Required]
        [Column(TypeName = "decimal(10,2)")]
        public decimal QuantitePrevue { get; set; }
        
        [Column(TypeName = "decimal(10,2)")]
        public decimal? QuantiteReelle { get; set; }
        
        [Column(TypeName = "decimal(10,2)")]
        public decimal? EcartAbsolu { get; set; }
        
        [Column(TypeName = "decimal(5,2)")]
        public decimal? EcartRelatif { get; set; }
        
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        
        public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    }
}