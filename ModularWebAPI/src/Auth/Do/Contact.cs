using System.ComponentModel.DataAnnotations;

namespace ModularWebAPI.Auth.Do
{
    public class Contact
    {
        [Key]
        public Guid Id { get; set; } = Guid.NewGuid();
        
        [Required]
        [StringLength(100)]
        public string Nom { get; set; } = string.Empty;
        
        [Required]
        [StringLength(100)]
        public string Prenom { get; set; } = string.Empty;
        
        [StringLength(20)]
        public string? Telephone { get; set; }
        
        [EmailAddress]
        [StringLength(255)]
        public string? Email { get; set; }
        
        [StringLength(100)]
        public string? Poste { get; set; }
        
        public Guid FournisseurId { get; set; }
        public Fournisseur Fournisseur { get; set; } = null!;
    }
}